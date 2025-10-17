import os
import sys
import json
from pathlib import Path
from typing import List

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECTIONS_JSONL = Path(os.getenv("SECTIONS_JSONL_PATH", str(BASE_DIR / "data" / "sections" / "sections.jsonl")))
EMBEDDINGS_JSONL = Path(os.getenv("EMBEDDINGS_JSONL_PATH", str(BASE_DIR / "data" / "embeddings" / "embeddings.jsonl")))

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
EMBEDDINGS_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", "text-embedding-ada-002")


def get_client():
    try:
        from openai import AzureOpenAI  # defer import for clearer error if missing
    except ImportError as ie:
        print("[ERROR] No se pudo importar openai. Instala dependencias en este entorno de Python (pip install -r 02_Embedding/requirements.txt)")
        raise
    if not ENDPOINT or not API_KEY:
        print("Faltan AZURE_OPENAI_ENDPOINT o AZURE_OPENAI_API_KEY en .env de 02_Embedding")
        sys.exit(1)
    return AzureOpenAI(
        api_key=API_KEY,
        api_version=API_VERSION,
        azure_endpoint=ENDPOINT,
    )


def load_sections(jsonl_path: Path) -> List[dict]:
    if not jsonl_path.exists():
        print(f"No existe {jsonl_path}. Ejecuta slice_sections.py y add_manual_chapter.py antes.")
        sys.exit(1)
    recs = []
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        recs.append(json.loads(line))
    return recs


def main() -> None:
    print(f"[INFO] SECTIONS_JSONL={SECTIONS_JSONL}")
    print(f"[INFO] EMBEDDINGS_JSONL={EMBEDDINGS_JSONL}")
    print(f"[INFO] Endpoint set={bool(ENDPOINT)} api_version={API_VERSION} deployment={EMBEDDINGS_DEPLOYMENT}")

    sections = load_sections(SECTIONS_JSONL)
    print(f"[INFO] Loaded sections: {len(sections)}")
    if not sections:
        print("[ERROR] No se encontraron secciones para embeddear. Revisa sections.jsonl")
        return

    client = get_client()

    EMBEDDINGS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with EMBEDDINGS_JSONL.open("w", encoding="utf-8") as out:
        for rec in sections:
            print(f"[INFO] Embedding id={rec.get('id')} title={rec.get('title')}")
            text = (rec.get("content") or "").strip()
            if not text:
                print(f"[WARN] id={rec.get('id')} title='{rec.get('title')}' está vacío. Se genera embedding de cadena vacía.")
            try:
                resp = client.embeddings.create(
                    model=EMBEDDINGS_DEPLOYMENT,
                    input=text,
                )
                vec = resp.data[0].embedding
            except Exception as e:
                print(f"[ERROR] Falló embedding para id={rec.get('id')} title='{rec.get('title')}': {e}")
                vec = []

            out.write(json.dumps({
                "id": rec.get("id"),
                "title": rec.get("title"),
                "embedding": vec,
            }, ensure_ascii=False) + "\n")

    print(f"Embeddings guardados en: {EMBEDDINGS_JSONL}")


if __name__ == "__main__":
    main()
