from openai import AzureOpenAI
from dotenv import load_dotenv
import os
import sys

# Calcular la raíz del proyecto (02_IntentClassification) y añadirla a sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from prompts.system_message import get_system_message
from prompts.user_message import get_user_message

# Cargar variables de entorno desde el .env del proyecto
dotenv_path = os.path.join(PROJECT_ROOT, '.env')
load_dotenv(dotenv_path=dotenv_path)

# Configuración del modelo
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
    # Frases de ejemplo
    examples_path = os.path.join(PROJECT_ROOT, "data", "examples.txt")
    with open(examples_path, "r", encoding="utf-8") as f:
        examples = f.readlines()

    results = []
    for example in examples:
        text = example.strip()

        # Construir mensajes de chat (system + user)
        system_msg = get_system_message()
        user_msg = get_user_message(text)
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]

        # Llamar al modelo GPT-4 (Chat Completions)
        response = client.chat.completions.create(
            model=DEPLOYMENT,  # nombre del deployment en Azure
            messages=messages,
            temperature=0,
            max_tokens=100,
        )

        # Procesar la salida directamente
        intent = (response.choices[0].message.content or "").strip()
        results.append({"input": example.strip(), "intent": intent})

        # Mostrar el resultado en consola
        print(f"Entrada: {example.strip()} -> Intención: {intent}")

    # Guardar resultados
    results_dir = os.path.join(PROJECT_ROOT, "data", "results")
    os.makedirs(results_dir, exist_ok=True)
    results_path = os.path.join(results_dir, "gpt-4-results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        import json
        json.dump(results, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()