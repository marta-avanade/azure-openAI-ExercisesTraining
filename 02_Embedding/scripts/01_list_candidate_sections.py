import os
import re
import json
from pathlib import Path
from typing import List, Set

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_JSON = BASE_DIR / "DocumentIntelligence" / "data" / "output.json"

SOURCE_JSON = Path(os.getenv("EMBEDDING_SOURCE_JSON", str(DEFAULT_JSON)))
OUTPUT_PATH = Path(os.getenv("CANDIDATE_SECTIONS_JSON", str(BASE_DIR / "data" / "candidate_sections.json")))


def is_title_candidate(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    # Length constraints
    if len(s) < 3 or len(s) > 120:
        return False
    # Reject lines that look like paragraphs (too many punctuation)
    if sum(ch in ",.;:!?" for ch in s) > 3:
        return False
    # If begins with Chapter/Capítulo variants
    if re.match(r"^(cap[ií]tulo|chapter)\b", s, flags=re.IGNORECASE):
        return True
    # ALL CAPS short-ish line
    letters = [c for c in s if c.isalpha()]
    if letters and s.upper() == s and len(s) <= 60:
        return True
    # Title Case heuristic: many words starting uppercase (Spanish titles often capitalize first word)
    words = [w for w in re.split(r"\s+", s) if w]
    if not words:
        return False
    cap_words = sum(1 for w in words if w[:1].isupper())
    if cap_words / max(1, len(words)) >= 0.6:
        return True
    return False


def collect_candidates(text_lines: List[str]) -> List[str]:
    seen: Set[str] = set()
    result: List[str] = []
    for ln in text_lines:
        if is_title_candidate(ln):
            key = ln.strip()
            if key not in seen:
                seen.add(key)
                result.append(key)
    return result


def main() -> None:
    if not SOURCE_JSON.exists():
        print(f"No se encontró el JSON de origen: {SOURCE_JSON}")
        print("Asegúrate de ejecutar primero DocumentIntelligence para generar output.json.")
        return

    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    pages = data.get("pages") or []

    lines: List[str] = []
    for p in pages:
        txt = p.get("text") or ""
        lines.extend(txt.splitlines())

    candidates = collect_candidates(lines)

    # Imprime candidatos en consola (Markdown-friendly)
    print("\nCandidatos detectados (revisa y elige 3):\n")
    for i, cand in enumerate(candidates, 1):
        print(f"{i}. {cand}")

    # Guarda también en JSON para referencia
    try:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps({"candidates": candidates}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nCandidatos guardados en: {OUTPUT_PATH}")
    except Exception as e:
        print(f"\nNo se pudo guardar candidate_sections.json: {e}")


if __name__ == "__main__":
    main()
