import os
import sys
from dotenv import load_dotenv
from time import sleep
from openai import AzureOpenAI
import re

# Calcular la raíz del proyecto (03_CategorizationClaims) y añadirla a sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Importar el builder de prompts desde el paquete local
from prompts.prompt_builder import build_prompt

# Cargar variables de entorno desde el .env del proyecto
dotenv_path = os.path.join(PROJECT_ROOT, '.env')
load_dotenv(dotenv_path=dotenv_path)

# Configuración del modelo (Azure OpenAI)
API_KEY = os.getenv("AZURE_OPENAI_API_KEY_GPT4")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT_GPT4")
API_VERSION = os.getenv("AZURE_API_VERSION") or os.getenv("AZURE_OPENAI_API_VERSION") or "2024-06-01"
DEPLOYMENT = os.getenv("OPENAI_MODEL4", "gpt-4")

# Inicializar cliente Azure OpenAI
client = AzureOpenAI(
    api_key=API_KEY,
    azure_endpoint=ENDPOINT,
    api_version=API_VERSION,
)

def main():
    # Frases de ejemplo (ruta relativa a la raíz del proyecto)
    examples_path = os.path.join(PROJECT_ROOT, "data", "examples.txt")
    with open(examples_path, "r", encoding="utf-8") as f:
        examples = f.readlines()

    print(f"Total de ejemplos: {len(examples)}")

    results = []
    for idx, example in enumerate(examples, start=1):
        # Normalizar texto: quitar viñetas '- ' y comillas envolventes si existen
        text = example.strip()
        # Quitar viñetas comunes: -, –, •
        text = re.sub(r"^\s*[-–•]\s*", "", text)
        if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
            text = text[1:-1].strip()

        # Saltar líneas vacías
        if not text:
            continue

        # Construir mensajes de chat (system + user)
        prompt = build_prompt(text)

        # Llamar al modelo GPT-4 (Chat Completions)
        try:
            response = client.chat.completions.create(
                model=DEPLOYMENT,  # nombre del deployment en Azure
                messages=prompt,
                temperature=0,
                max_tokens=100,
            )
        except Exception as e:
            print(f"[{idx}/{len(examples)}] Error al llamar al modelo: {e}")
            # Intento simple de backoff si es rate limit
            sleep(2)
            continue

        # Procesar la salida: se espera JSON con categoria y subcategoria
        raw = (response.choices[0].message.content or "").strip()
        categoria = None
        subcategoria = None
        try:
            import json
            parsed = json.loads(raw)
            categoria = parsed.get("categoria")
            subcategoria = parsed.get("subcategoria")
        except Exception:
            # fallback si el modelo no devolvió JSON válido
            categoria = raw
            subcategoria = None

        results.append({
            "input": example.strip(),
            "categoria": categoria,
            "subcategoria": subcategoria,
            "raw": raw,
        })

        # Mostrar el resultado en consola
        print(f"[{idx}/{len(examples)}] Entrada: {text} -> Categoría: {categoria} | Subcategoría: {subcategoria}")

    # Guardar resultados
    results_dir = os.path.join(PROJECT_ROOT, "data", "results")
    os.makedirs(results_dir, exist_ok=True)
    results_path = os.path.join(results_dir, "gpt-4-results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        import json
        json.dump(results, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()