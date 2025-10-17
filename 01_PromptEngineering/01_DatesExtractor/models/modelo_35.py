"""
Cliente para ejecutar prompts contra Azure OpenAI (deployment gpt-35-turbo)
y guardar las respuestas en JSON.

Responsabilidades del módulo:
- Cargar variables de entorno desde 01_DatesExtractor/.env
- Importar prompts (system_message y user_messages)
- Invocar el endpoint de Azure OpenAI usando el SDK oficial (openai.AzureOpenAI)
- Guardar los resultados en results/{OPENAI_MODEL}.json
"""

import os
import json
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from openai import AzureOpenAI

# Permitir ejecutar este archivo directamente (evita el error de importación relativa)
try:
    from ..prompts.prompts import system_message, user_messages  # type: ignore
except Exception:
    import sys
    from pathlib import Path
    CURRENT_DIR = Path(__file__).resolve().parent 
    PACKAGE_ROOT = CURRENT_DIR.parent  # .../01_DatesExtractor
    if str(PACKAGE_ROOT) not in sys.path:
        sys.path.insert(0, str(PACKAGE_ROOT))
    from prompts.prompts import system_message, user_messages

# Cargar las credenciales desde el archivo .env ubicado en la raíz de 01_DatesExtractor
BASE_DIR = Path(__file__).resolve().parent.parent  # .../01_DatesExtractor
ENV_PATH = BASE_DIR / ".env" 
_loaded = load_dotenv(ENV_PATH)  # devuelve True si se cargó

def _getenv_any(names):
    for n in names:
        val = os.getenv(n)
        if val:
            return val
    return None

# Variables de entorno específicas para GPT-3.5 (con fallback a generales)
OPENAI_API_KEY = _getenv_any(["AZURE_OPENAI_API_KEY_GPT35", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_KEY", "OPENAI_API_KEY"])  
# Nombre del deployment en Azure: prioriza OPENAI_MODEL35 para 3.5
OPENAI_MODEL = _getenv_any(["OPENAI_MODEL35", "OPENAI_MODEL"]) or "gpt-35-turbo"
AZURE_OPENAI_ENDPOINT = _getenv_any(["AZURE_OPENAI_ENDPOINT_GPT35", "AZURE_OPENAI_ENDPOINT", "OPENAI_API_BASE", "AZURE_OPENAI_ENDPOINT_URL"])  # https://<recurso>.openai.azure.com/
AZURE_API_VERSION = (_getenv_any(["AZURE_API_VERSION", "AZURE_OPENAI_API_VERSION", "OPENAI_API_VERSION"]) or "2025-01-01-preview").strip()

if not OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
    missing = []
    if not OPENAI_API_KEY:
        missing.append("AZURE_OPENAI_API_KEY/AZURE_OPENAI_KEY/OPENAI_API_KEY")
    if not AZURE_OPENAI_ENDPOINT:
        missing.append("AZURE_OPENAI_ENDPOINT/OPENAI_API_BASE")
    raise ValueError(
        "Faltan variables de entorno: "
        + ", ".join(missing)
        + (f". Se intentó cargar: {ENV_PATH} (existente={ENV_PATH.exists()}, cargado={_loaded})")
    )

# Instanciar el cliente de Azure OpenAI (SDK oficial de OpenAI)
client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_API_VERSION,
)

def llamar_modelo_35():
    """
    Ejecuta el chat con el deployment (modelo) configurado y devuelve respuestas.

    Returns: 
        list[dict]: Lista con objetos {"input": str, "output": str} 
    """
    resultados = []

    for user_msg in user_messages:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,  # En Azure, este es el deployment name
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_msg},
            ],
        )
        content = resp.choices[0].message.content.strip() if resp.choices else ""
        resultados.append({"input": user_msg, "output": content})

    return resultados

def guardar_resultados_en_json(resultados: List[Dict[str, str]], modelo: str) -> str:
    """
    Guarda los resultados en un archivo JSON en la carpeta results.

    Args:
        resultados (list[dict]): Lista de resultados con input/output.
        modelo (str): Nombre del deployment (modelo) utilizado.
    """
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent  # .../01_DatesExtractor
    results_dir = base_dir / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    # Sanitizar nombre de archivo para evitar caracteres raros
    safe_model = "".join(c for c in modelo if c.isalnum() or c in ("-", "_", "."))
    file_path = results_dir / f"{safe_model}.json"
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(resultados, json_file, ensure_ascii=False, indent=2)

    return str(file_path)

if __name__ == "__main__":
    resultados = llamar_modelo_35()
    out_path = guardar_resultados_en_json(resultados, OPENAI_MODEL)
    print(f"Resultados guardados en: {out_path}")