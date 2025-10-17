import os
import sys
import json
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECTIONS_JSONL = Path(os.getenv("SECTIONS_JSONL_PATH", str(BASE_DIR / "data" / "sections" / "sections.jsonl")))
DEFAULT_TITLE = os.getenv("MANUAL_CHAPTER_TITLE", "IV. Appendices")
DEFAULT_TEXT_FILE = Path(os.getenv("MANUAL_CHAPTER_FILE", str(BASE_DIR / "data" / "manual_chapter.txt")))


def main() -> None:
    parser = argparse.ArgumentParser(description="Añade un capítulo manual al .jsonl de secciones")
    parser.add_argument("--title", required=False, default=DEFAULT_TITLE, help="Título EXACTO del capítulo a añadir (por defecto: env MANUAL_CHAPTER_TITLE o 'IV. Appendices')")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("--text", help="Contenido del capítulo (texto directo)")
    group.add_argument("--text-file", dest="text_file", help=f"Ruta a un .txt con el contenido del capítulo (por defecto: {DEFAULT_TEXT_FILE})")

    args = parser.parse_args()

    if not SECTIONS_JSONL.exists():
        print(f"No existe el archivo de secciones: {SECTIONS_JSONL}. Ejecuta primero slice_sections.py")
        sys.exit(1)

    # Determinar contenido por prioridad: --text-file > --text > DEFAULT_TEXT_FILE
    content = None
    if args.text_file:
        tf = Path(args.text_file)
        if not tf.exists():
            print(f"No existe el archivo de texto: {tf}")
            sys.exit(1)
        content = tf.read_text(encoding="utf-8")
    elif args.text is not None:
        content = args.text
    else:
        # Fallback al archivo por defecto
        if not DEFAULT_TEXT_FILE.exists():
            print(f"No se proporcionó --text/--text-file y no existe el archivo por defecto: {DEFAULT_TEXT_FILE}")
            print("Crea el archivo o indica --text-file.")
            sys.exit(1)
        content = DEFAULT_TEXT_FILE.read_text(encoding="utf-8")

    title = (args.title or DEFAULT_TITLE).strip()
    if not title:
        print("El título está vacío. Indica --title o configura MANUAL_CHAPTER_TITLE.")
        sys.exit(1)

    # Lee para calcular el próximo id
    lines = SECTIONS_JSONL.read_text(encoding="utf-8").splitlines()
    next_id = 1
    if lines:
        try:
            last = json.loads(lines[-1])
            next_id = int(last.get("id", len(lines))) + 1
        except Exception:
            next_id = len(lines) + 1

    rec = {
        "id": next_id,
        "title": title,
        "start_page": None,
        "end_page": None,
        "content": content,
    }

    with SECTIONS_JSONL.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Capítulo añadido con id={next_id} en {SECTIONS_JSONL}")
    print(f"Título: {title}")
    if args.text_file:
        print(f"Fuente: {args.text_file}")
    elif args.text is not None:
        print("Fuente: --text (inline)")
    else:
        print(f"Fuente: {DEFAULT_TEXT_FILE}")


if __name__ == "__main__":
    main()
