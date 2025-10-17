"""Runner para ejecutar el modelo GPT-35 (Azure OpenAI) con OpenAI >= 1.x.

Incluye:
- Carga de .env
- Ajuste de sys.path para imports relativos del ejercicio
- Cliente AzureOpenAI
- Construcción de mensajes, llamada al modelo y parseo robusto de JSON
"""

import os
import sys
import json
from typing import Any, List, Dict
from datetime import datetime

from dotenv import load_dotenv  # type: ignore
from openai import AzureOpenAI

# Añadir la raíz del proyecto a sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from prompts.prompt_builder import build_prompt
from utils.parser import parse_output
from utils.entity_types import get_entity_types

# Nombre del modelo (deployment) en Azure OpenAI
MODEL_NAME = "gpt-35-turbo"

def get_client() -> AzureOpenAI:
    """Inicializa el cliente de Azure OpenAI usando variables de entorno.

    Requiere:
    - OPENAI_API_KEY (o AZURE_OPENAI_API_KEY)
    - AZURE_OPENAI_ENDPOINT (o gpt35_endpoint/gpt4_endpoint como fallback)
    - AZURE_OPENAI_API_VERSION (por ejemplo, 2024-02-15-preview)
    """
    load_dotenv()  # Carga .env si existe

    api_key = os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta la API key. Define AZURE_OPENAI_API_KEY u OPENAI_API_KEY en .env")

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("gpt35_endpoint") or os.getenv("gpt4_endpoint")
    if not endpoint:
        raise RuntimeError("Falta el endpoint de Azure. Define AZURE_OPENAI_ENDPOINT en .env")

    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    return AzureOpenAI(api_key=api_key, azure_endpoint=endpoint, api_version=api_version)


def _get_env_config() -> Dict[str, str]:
    """Devuelve configuración relevante del entorno para guardar en el output."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") or os.getenv("gpt35_endpoint") or os.getenv("gpt4_endpoint") or ""
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "")
    return {"endpoint": endpoint, "api_version": api_version}

def run_gpt35(system_message, user_message, input_text) -> Dict[str, Any]:
    """
    Ejecuta el modelo GPT-35 con los mensajes proporcionados.

    Args:
        system_message (str): Mensaje del sistema.
        user_message (str): Mensaje del usuario.
        input_text (str): Texto de entrada.

    Returns:
        dict: Respuesta del modelo.
    """
    client = get_client()

    # Definición de herramienta (function calling) para forzar salida estructurada
    tools = [
        {
            "type": "function",
            "function": {
                "name": "return_entities",
                "description": "Devuelve las entidades extraídas",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "keyword": {"type": "string"},
                                    "type": {
                                        "type": "string",
                                        "enum": ["Concepto", "Localización", "Tiempo"],
                                    },
                                },
                                "required": ["keyword", "type"],
                            },
                        }
                    },
                    "required": ["entities"],
                },
            },
        }
    ]

    prompt = build_prompt(system_message, user_message, input_text)
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "return_entities"}},
        temperature=0,
    )

    message = resp.choices[0].message if resp.choices else None
    content = message.content if message else ""

    # Prioridad 1: tool_calls (function calling)
    parsed_list: List[Any] = []
    origin = ""
    if message and getattr(message, "tool_calls", None):
        for tc in message.tool_calls:
            try:
                if tc.type == "function" and tc.function and tc.function.name == "return_entities":
                    args = tc.function.arguments or "{}"
                    data = json.loads(args)
                    if isinstance(data, dict) and isinstance(data.get("entities"), list):
                        parsed_list = data["entities"]
                        origin = "tool_call"
                        break
            except Exception:
                continue

    # Prioridad 2: contenido JSON puro
    if not parsed_list and content:
        try:
            maybe = json.loads(content)
            if isinstance(maybe, list):
                parsed_list = maybe
                origin = "model_json"
        except Exception:
            parsed_list = []

    # Validar/normalizar con el parser (si hay lista)
    cleaned = parse_output(parsed_list) if parsed_list else []

    # Heurística: si el modelo respondió en viñetas estilo
    # "- Concepto: ...", intentar mapear a la estructura
    if not cleaned and any(h in content for h in [
        "- Concepto:", "- Localización:", "- Localizacion:", "- Tiempo:",
        "Concepto:", "Localización:", "Localizacion:", "Tiempo:"
    ]):
        heur = _heuristic_to_entities(content)
        cleaned = parse_output(heur)
        if cleaned:
            origin = "heuristic"

    return {"raw_text": content, "parsed": cleaned, "origin": origin}


def _format_console_row(input_text: str, parsed: Any, raw_text: str) -> str:
    """Devuelve una fila Markdown tipo | entrada | `json` | ajustando Localización -> Localizacion."""
    # Preferimos la lista parseada si existe; si no, intentamos usar raw_text si es JSON válido
    display_obj: Any = parsed if parsed else None
    if display_obj is None:
        try:
            tmp = json.loads(raw_text)
            if isinstance(tmp, (list, dict)):
                display_obj = tmp
        except Exception:
            display_obj = raw_text

    if isinstance(display_obj, (list, dict)):
        s = json.dumps(display_obj, ensure_ascii=False)
    else:
        s = str(display_obj)

    # Ajuste estético: sin tilde, como en README de ejemplo
    s = s.replace("Localización", "Localizacion")
    return f"| {input_text} | `{s}` |"


def _heuristic_to_entities(text: str) -> List[Dict[str, str]]:
    """Convierte una salida con viñetas '- Tipo: valores' a lista de entidades.

    Ejemplos que maneja:
    - "- Concepto: saldo vivo"
    - "- Concepto: Dirección Territorial, dudoso."
    - "- Localización: No hay entidades de localización en este texto."
    - "- Tiempo: septiembre de 2023"
    """
    raw_lines = [ln.rstrip() for ln in text.splitlines()]
    results: List[Dict[str, str]] = []

    def norm_type(t_raw: str) -> str:
        t = t_raw.strip().lower()
        if t.startswith("localiz"):
            return "Localización"
        if t.startswith("concepto"):
            return "Concepto"
        if t.startswith("tiempo"):
            return "Tiempo"
        return ""

    # Dos modos: inline (- Tipo: valores) y secciones (Tipo:\n- item) mezclados
    current_type: str = ""
    for ln in raw_lines:
        s = ln.strip()
        if not s:
            continue

        # Detectar encabezado de sección: 'Concepto:' 'Localización:' 'Tiempo:'
        if s.endswith(":") and not s.startswith("-"):
            t = norm_type(s[:-1])
            current_type = t
            continue

        # Modo inline: '- Tipo: valores'
        if s.startswith("-") and ":" in s:
            dash_removed = s[1:].strip()
            # Puede ser '- palabra' (bullet bajo sección) o '- Tipo: valores'
            before, after = dash_removed.split(":", 1)
            maybe_type = norm_type(before)
            if maybe_type:
                # Inline con tipo explícito
                t_norm = maybe_type
                content = after.strip()
                low = content.lower()
                if low.startswith("no hay") or low in {"no aplica", "n/a", "na", "no aplica."}:
                    continue
                content = content.rstrip(".")
                parts = [p.strip() for p in content.split(",") if p.strip()]
                for p in parts:
                    results.append({"keyword": p, "type": t_norm})
                current_type = ""  # Reseteamos para evitar arrastre accidental
                continue
            else:
                # Bullet simple bajo la sección actual
                if not current_type:
                    continue
                item = dash_removed.strip()
                lowi = item.lower()
                if lowi.startswith("no hay") or lowi in {"no aplica", "n/a", "na", "no aplica."}:
                    continue
                item = item.rstrip(".")
                if item:
                    results.append({"keyword": item, "type": current_type})
                continue

        # Si es una línea simple (no bullet) sin encabezado, ignorar
        # También ignoramos textos introductorios tipo 'Entidades clasificadas:'
        continue

    return results

def main():
    """
    Punto de entrada principal para ejecutar el script.
    """
    from prompts.system_message import get_system_message
    from prompts.user_message import get_user_message

    system_message = get_system_message()
    user_message = get_user_message()

    # Cargar entradas desde data/input_data.json
    data_path = os.path.join(PROJECT_ROOT, "data", "input_data.json")
    with open(data_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    examples = payload.get("examples", [])

    results = []
    # Imprimir solo filas (formato exacto como en el README del ejemplo)

    for text in examples:
        try:
            output = run_gpt35(system_message, user_message, text)
        except Exception as e:
            # Si hay fallo, representamos raw y parsed vacíos
            output = {"raw_text": f"<error: {e}>", "parsed": []}

        # Fila en consola, exactamente: | entrada | `[...]` |
        print(_format_console_row(text, output.get("parsed"), output.get("raw_text", "")))

        results.append({
            "input": text,
            "output": {
                "raw_text": output.get("raw_text"),
                "parsed": output.get("parsed", []),
                "origin": output.get("origin", ""),
            }
        })

    # Guardar en archivo de salida con nombre del modelo
    safe_model = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in MODEL_NAME)
    out_path = os.path.join(PROJECT_ROOT, "data", f"output_data_{safe_model}.json")
    env_cfg = _get_env_config()
    structured_output = {
        "model": MODEL_NAME,
        "endpoint": env_cfg.get("endpoint", ""),
        "api_version": env_cfg.get("api_version", ""),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input_summary": {"total": len(examples)},
        "results": results,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(structured_output, f, ensure_ascii=False, indent=2)
    print(f"\nResultados guardados en: {out_path}")

if __name__ == "__main__":
    main()