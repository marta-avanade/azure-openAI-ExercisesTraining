import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import List, Tuple

import numpy as np
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECTIONS_JSONL = Path(os.getenv("SECTIONS_JSONL_PATH", str(BASE_DIR / "data" / "sections" / "sections.jsonl")))
EMBEDDINGS_JSONL = Path(os.getenv("EMBEDDINGS_JSONL_PATH", str(BASE_DIR / "data" / "embeddings" / "embeddings.jsonl")))
QA_RUNS_JSONL = Path(os.getenv("QA_RUNS_JSONL_PATH", str(BASE_DIR / "data" / "logs" / "qa_runs.jsonl")))

ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
EMBEDDINGS_DEPLOYMENT = os.getenv("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT", "text-embedding-ada-002")
CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")


def get_client():
    try:
        from openai import AzureOpenAI
    except ImportError:
        print("[ERROR] Falta la librería 'openai'. Instálala en este entorno (pip install -r 02_Embedding/requirements.txt)")
        sys.exit(1)
    if not ENDPOINT or not API_KEY:
        print("[ERROR] Faltan AZURE_OPENAI_ENDPOINT o AZURE_OPENAI_API_KEY en 02_Embedding/.env")
        sys.exit(1)
    return AzureOpenAI(api_key=API_KEY, api_version=API_VERSION, azure_endpoint=ENDPOINT)


def load_jsonl(path: Path) -> List[dict]:
    if not path.exists():
        print(f"[ERROR] No existe: {path}")
        sys.exit(1)
    recs: List[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            recs.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"[WARN] Línea inválida en {path}: {e}")
    return recs


def as_np(v: List[float]) -> np.ndarray:
    if v is None:
        return np.zeros((1,), dtype=np.float32)
    arr = np.array(v, dtype=np.float32)
    return arr


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return -1.0
    # Normaliza y calcula coseno
    a_norm = a / (np.linalg.norm(a) + 1e-10)
    b_norm = b / (np.linalg.norm(b) + 1e-10)
    return float(np.dot(a_norm, b_norm))


def embed_query(client, text: str) -> np.ndarray:
    resp = client.embeddings.create(model=EMBEDDINGS_DEPLOYMENT, input=text)
    return as_np(resp.data[0].embedding)


def retrieve_top_k(query_vec: np.ndarray, embedding_recs: List[dict], k: int = 3) -> List[Tuple[int, float]]:
    scores: List[Tuple[int, float]] = []
    for idx, rec in enumerate(embedding_recs):
        vec = as_np(rec.get("embedding") or [])
        s = cosine_sim(query_vec, vec)
        scores.append((idx, s))
    # Ordena por score descendente
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:max(1, k)]


def build_prompt(context_chunks: List[dict], question: str) -> List[dict]:
    context_blocks = []
    for ch in context_chunks:
        title = ch.get("title")
        content = ch.get("content", "")
        context_blocks.append(f"[Titulo: {title}]\n{content}")
    context_text = "\n\n---\n\n".join(context_blocks)

    system = (
        "Eres un asistente que responde con precisión usando solo el contexto proporcionado. "
        "Si la respuesta no está en el contexto, di claramente que no aparece en el documento."
    )
    user = (
        f"Contexto:\n{context_text}\n\n"
        f"Pregunta: {question}\n\n"
        "Responde de forma breve (3-6 frases) e incluye referencias entre corchetes con el título de la sección relevante."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def answer_with_chat(client, messages: List[dict], max_tokens: int = 300, temperature: float = 0.1) -> str:
    if not CHAT_DEPLOYMENT:
        return "[ERROR] Falta AZURE_OPENAI_CHAT_DEPLOYMENT en .env para generar una respuesta."
    try:
        resp = client.chat.completions.create(
            model=CHAT_DEPLOYMENT,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        return f"[ERROR] Falló la generación de respuesta: {e}"


def main():
    parser = argparse.ArgumentParser(description="RAG Q&A sobre sections.jsonl + embeddings.jsonl")
    parser.add_argument("-q", "--question", type=str, help="Pregunta a realizar")
    parser.add_argument("-k", "--top-k", type=int, default=3, help="Número de fragmentos a recuperar")
    parser.add_argument("--max-tokens", type=int, default=300, help="Límite de tokens de salida")
    parser.add_argument("--temperature", type=float, default=0.1, help="Temperatura de la respuesta")
    args = parser.parse_args()

    client = get_client()

    sections = load_jsonl(SECTIONS_JSONL)
    embeddings = load_jsonl(EMBEDDINGS_JSONL)

    if not sections:
        print("[ERROR] sections.jsonl vacío")
        sys.exit(1)
    if not embeddings:
        print("[ERROR] embeddings.jsonl vacío")
        sys.exit(1)

    if len(sections) != len(embeddings):
        print(f"[WARN] Tamaños distintos: sections={len(sections)} embeddings={len(embeddings)}. Se usará el mínimo común por posición.")
        n = min(len(sections), len(embeddings))
        sections = sections[:n]
        embeddings = embeddings[:n]

    question = args.question or input("Pregunta: ").strip()
    if not question:
        print("[ERROR] Pregunta vacía")
        sys.exit(1)

    print("[INFO] Generando embedding de la consulta…")
    q_vec = embed_query(client, question)

    print("[INFO] Recuperando fragmentos relevantes…")
    top = retrieve_top_k(q_vec, embeddings, k=args.top_k)
    chosen = [sections[i] for (i, _score) in top]

    messages = build_prompt(chosen, question)
    print("[INFO] Llamando al modelo de chat…")
    answer = answer_with_chat(client, messages, max_tokens=args.max_tokens, temperature=args.temperature)

    # Persistencia del run
    QA_RUNS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": int(time.time()),
        "question": question,
        "top_k": args.top_k,
        "indices": [i for (i, _s) in top],
        "scores": [float(s) for (_i, s) in top],
        "titles": [sections[i].get("title") for (i, _s) in top],
        "answer": answer,
    }
    with QA_RUNS_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("\n===== RESPUESTA =====\n")
    print(answer)


if __name__ == "__main__":
    main()
