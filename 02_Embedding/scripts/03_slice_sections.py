import os
import sys
import json
from pathlib import Path
from typing import List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    from config import section_list
except Exception as e:
    print(f"No se pudo importar section_list desde config.py: {e}")
    sys.exit(1)

SOURCE_JSON = Path(os.getenv("EMBEDDING_SOURCE_JSON", str(BASE_DIR / "DocumentIntelligence" / "data" / "output.json")))
SECTIONS_JSONL = Path(os.getenv("SECTIONS_JSONL_PATH", str(BASE_DIR / "data" / "sections" / "sections.jsonl")))


def _is_toc_page(text: str) -> bool:
    """Heurística simple para detectar páginas de índice/tabla de contenidos."""
    lowered = text.lower()
    toc_hints = (
        "table of contents",
        "contents",
        "indice",
        "índice",
    )
    return any(h in lowered for h in toc_hints)


def _find_title_first_page(title: str, pages: List[dict]) -> int:
    """Devuelve el índice de página (0-based) donde aparece el título, o -1 si no aparece.
    Se busca coincidencia exacta por línea (con strip()). Evita páginas de índice (ToC).
    """
    t = title.strip()
    first_anywhere = -1
    for idx, page in enumerate(pages):
        text = page.get("text") or ""
        for line in text.splitlines():
            if line.strip() == t:
                # Guarda la primera coincidencia global por si todas están en ToC
                if first_anywhere == -1:
                    first_anywhere = idx
                # Si esta página no parece ser índice, úsala
                if not _is_toc_page(text):
                    return idx
                break
    # Si solo se encontró en ToC, devolver esa coincidencia como fallback
    return first_anywhere


def _slice_by_titles(pages: List[dict], titles_in_order: List[str]) -> List[dict]:
    # Encuentra página de inicio para cada título
    starts: List[int] = []
    for t in titles_in_order:
        pidx = _find_title_first_page(t, pages)
        starts.append(pidx)

    # Empaqueta secciones; si un título no aparece, crea sección vacía
    sections = []
    last_page_idx = len(pages)
    for i, t in enumerate(titles_in_order):
        start = starts[i]
        # Busca el siguiente inicio que sea estrictamente mayor que "start"
        end = last_page_idx
        if i + 1 < len(starts):
            for j in range(i + 1, len(starts)):
                if starts[j] != -1 and (start == -1 or starts[j] > start):
                    end = starts[j]
                    break

        if start == -1:
            # No encontrado
            content = ""
            start_page = None
            end_page = None
            warning = f"[WARN] Título no encontrado en el documento: {t}"
            print(warning)
        else:
            # Ajusta end si es -1 (ningún siguiente título encontrado)
            if end == -1:
                end = last_page_idx
            # Concatena texto de páginas [start, end)
            content = "\n".join((pages[j].get("text") or "") for j in range(start, max(start, end)))
            start_page = start + 1  # 1-based para humanos
            end_page = max(start, end)  # exclusive index -> mostrar como índice 1-based del final real

        sections.append({
            "title": t,
            "start_page": start_page,
            "end_page": end_page,
            "content": content,
        })
    return sections


def main() -> None:
    if not SOURCE_JSON.exists():
        print(f"No se encontró el JSON de origen: {SOURCE_JSON}")
        print("Asegúrate de ejecutar primero DocumentIntelligence para generar output.json.")
        sys.exit(1)

    if not section_list or len(section_list) != 3:
        print("config.section_list debe contener exactamente 3 títulos (Paso 2).")
        sys.exit(1)

    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    pages = data.get("pages") or []

    sections = _slice_by_titles(pages, section_list)

    SECTIONS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with SECTIONS_JSONL.open("w", encoding="utf-8") as f:
        for i, sec in enumerate(sections, 1):
            rec = {
                "id": i,
                "title": sec["title"],
                "start_page": sec["start_page"],
                "end_page": sec["end_page"],
                "content": sec["content"],
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Secciones guardadas en: {SECTIONS_JSONL}")


if __name__ == "__main__":
    main()
