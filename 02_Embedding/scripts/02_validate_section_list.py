import os
import sys
import json
import difflib
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

try:
    from config import section_list
except Exception as e:
    print(f"No se pudo importar section_list desde config.py: {e}")
    sys.exit(1)

SOURCE_JSON = Path(os.getenv("EMBEDDING_SOURCE_JSON", str(BASE_DIR / "DocumentIntelligence" / "data" / "output.json")))


def main() -> None:
    if not SOURCE_JSON.exists():
        print(f"No se encontró el JSON de origen: {SOURCE_JSON}")
        print("Asegúrate de ejecutar primero DocumentIntelligence para generar output.json.")
        sys.exit(1)

    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    pages = data.get("pages") or []

    # Construye un 'haystack' con todo el texto
    full_text = "\n".join([p.get("text") or "" for p in pages])

    if not section_list:
        print("section_list está vacío en config.py. Añade 3 títulos exactos de capítulo.")
        sys.exit(1)

    # Genera lista de líneas únicas para sugerencias
    unique_lines: List[str] = []
    seen = set()
    for p in pages:
        for ln in (p.get("text") or "").splitlines():
            s = ln.strip()
            if s and s not in seen:
                seen.add(s)
                unique_lines.append(s)

    print("\nValidación de section_list (búsqueda exacta en el JSON):\n")
    for title in section_list:
        ok = title in full_text
        if ok:
            print(f"✔ Encontrado: {title}")
        else:
            print(f"✖ No encontrado: {title}")
            # Sugerencias cercanas
            matches = difflib.get_close_matches(title, unique_lines, n=5, cutoff=0.6)
            if matches:
                print("   Sugerencias cercanas:")
                for m in matches:
                    print(f"   - {m}")

    print("\nConsejo: Copia/pega EXACTAMENTE el título desde los candidatos o desde el JSON para evitar diferencias de espacios/acentos.")


if __name__ == "__main__":
    main()
