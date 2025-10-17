import os
import json
from pathlib import Path
from config import section_list

BASE_DIR = Path(__file__).resolve().parent.parent
# Permite override por variable de entorno para mantener consistencia con el resto de scripts
SOURCE_JSON = Path(os.getenv(
    "EMBEDDING_SOURCE_JSON",
    str(BASE_DIR / "DocumentIntelligence" / "data" / "output.json"),
))


def is_toc_page(text: str) -> bool:
    lowered = (text or "").lower()
    return any(x in lowered for x in ["table of contents", "contents", "indice", "índice"])  # naive heuristic


def run():
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    pages = data.get("pages") or []

    for title in section_list:
        t = title.strip()
        found_any = []
        print(f"\n== Title: {t}")
        for idx, page in enumerate(pages):
            text = page.get("text") or ""
            for line in text.splitlines():
                if line.strip() == t:
                    found_any.append((idx, is_toc_page(text), line))
                    break
        if not found_any:
            print("No matches found in any page.")
        else:
            for idx, is_toc, line in found_any:
                preview = (pages[idx].get("text") or "").splitlines()[0:5]
                print(f"- Page {idx+1} (toc={is_toc}) line='{line}' | first lines: {preview}")


if __name__ == "__main__":
    run()
