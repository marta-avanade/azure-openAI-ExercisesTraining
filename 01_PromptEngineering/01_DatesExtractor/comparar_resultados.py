"""Comparador de resultados entre GPT-3.5 y GPT-4 para Dates Extractor.

Lee los JSON generados en results/{modelo}.json y resume:
- Fechas únicas de cada modelo
- Fechas comunes
- Entradas con diferencias
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

def _load_results(file_path: Path) -> List[Dict[str, str]]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def _normalize_output(output: str) -> List[str]:
    """Intenta parsear la salida del modelo como lista de fechas.
    Si no es JSON válido, hace una limpieza simple por líneas y comas.
    Devuelve fechas en minúsculas y sin espacios extra.
    """
    output = output.strip()
    if not output:
        return []
    try:
        data = json.loads(output)
        if isinstance(data, list):
            return [str(x).strip().lower() for x in data]
    except Exception:
        pass
    # fallback: separar por saltos de línea o comas
    parts = [p.strip().lower() for p in output.replace("\n", ",").split(",")]
    return [p for p in parts if p]

def comparar_resultados(path_35: Path, path_4: Path) -> Dict[str, Any]:
    r35 = _load_results(path_35)
    r4 = _load_results(path_4)

    # Se asume misma cantidad de entradas (mismos text_examples)
    paired = list(zip(r35, r4))

    diffs = []
    comunes = set()
    solo_35 = set()
    solo_4 = set()

    for idx, (a, b) in enumerate(paired, start=1):
        a_list = _normalize_output(a.get("output", ""))
        b_list = _normalize_output(b.get("output", ""))

        s_a, s_b = set(a_list), set(b_list)
        comunes |= (s_a & s_b)
        solo_35 |= (s_a - s_b)
        solo_4 |= (s_b - s_a)

        if s_a != s_b:
            diffs.append({
                "case": idx,
                "input": a.get("input", "")[:120],
                "gpt35": sorted(s_a),
                "gpt4": sorted(s_b),
                "solo_gpt35": sorted(s_a - s_b),
                "solo_gpt4": sorted(s_b - s_a),
            })

    return {
        "comunes": sorted(comunes),
        "solo_gpt35": sorted(solo_35),
        "solo_gpt4": sorted(solo_4),
        "diferencias_por_caso": diffs,
    }

if __name__ == "__main__":
    path_35 = RESULTS_DIR / "gpt-35-turbo.json"
    path_4 = RESULTS_DIR / "gpt-4.json"
    summary = comparar_resultados(path_35, path_4)
    print(json.dumps(summary, ensure_ascii=False, indent=2))