"""
Cliente para ejecutar prompts contra Azure OpenAI usando el deployment GPT-4
y guardar las respuestas en JSON.
"""

import os
import json
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from openai import AzureOpenAI

# Importar prompts con relativa y fallback absoluto si se ejecuta como script
try:
    from ..prompts.prompts import system_message, user_messages  # type: ignore
except Exception:
    import sys
    CURRENT_DIR = Path(__file__).resolve().parent
    PACKAGE_ROOT = CURRENT_DIR.parent  # .../01_DatesExtractor
    if str(PACKAGE_ROOT) not in sys.path:
        sys.path.insert(0, str(PACKAGE_ROOT))
    from prompts.prompts import system_message, user_messages

# Cargar .env desde la raíz de 01_DatesExtractor
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
_loaded = load_dotenv(ENV_PATH)

def _getenv_any(names: List[str]) -> str | None:
    for n in names:
        v = os.getenv(n)
        if v:
            return v
    return None

# Variables necesarias: clave, endpoint, versión API y deployment (modelo)
OPENAI_API_KEY = _getenv_any(["AZURE_OPENAI_API_KEY_GPT4", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_KEY", "OPENAI_API_KEY"]) 
OPENAI_MODEL = _getenv_any(["OPENAI_MODEL4", "OPENAI_MODEL"]) or "gpt-4"  # nombre del deployment
AZURE_OPENAI_ENDPOINT = _getenv_any(["AZURE_OPENAI_ENDPOINT_GPT4", "AZURE_OPENAI_ENDPOINT", "OPENAI_API_BASE"]) 
AZURE_API_VERSION = _getenv_any(["AZURE_API_VERSION", "AZURE_OPENAI_API_VERSION"]) or "2025-01-01-preview"

missing = []
if not OPENAI_API_KEY:
    missing.append("AZURE_OPENAI_API_KEY/AZURE_OPENAI_KEY/OPENAI_API_KEY")
if not AZURE_OPENAI_ENDPOINT:
    missing.append("AZURE_OPENAI_ENDPOINT/OPENAI_API_BASE")
if missing:
    raise ValueError(
        "Faltan variables de entorno: " + ", ".join(missing) + f". Se intentó cargar: {ENV_PATH} (existente={ENV_PATH.exists()}, cargado={_loaded})"
    )

# Cliente Azure OpenAI (SDK openai)
client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_API_VERSION,
)

def llamar_modelo_4() -> List[Dict[str, str]]:
    """Ejecuta los prompts contra el deployment GPT-4 y devuelve
    una lista de objetos {input, output}.
    """
    resultados: List[Dict[str, str]] = []
    for user_msg in user_messages:
        try:
            resp = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_msg},
                ],
            )
            content = resp.choices[0].message.content.strip() if resp.choices else ""
        except Exception as e:
            content = f"<error: {type(e).__name__}: {e}>"
        resultados.append({"input": user_msg, "output": content})
    return resultados

def guardar_resultados_en_json(resultados: List[Dict[str, str]], modelo: str) -> str:
    """Guarda los resultados en results/{modelo}.json y devuelve la ruta."""
    results_dir = (Path(__file__).resolve().parent.parent / "results")
    results_dir.mkdir(parents=True, exist_ok=True)
    safe_model = "".join(c for c in modelo if c.isalnum() or c in ("-", "_", "."))
    file_path = results_dir / f"{safe_model}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    return str(file_path)

if __name__ == "__main__":
    resultados = llamar_modelo_4()
    out_path = guardar_resultados_en_json(resultados, OPENAI_MODEL)
    print(f"Resultados guardados en: {out_path}")