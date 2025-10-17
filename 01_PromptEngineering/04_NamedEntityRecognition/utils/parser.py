"""Parsers para validar/normalizar la salida del modelo."""

from typing import Any, List, Dict

from .entity_types import get_entity_types


ALLOWED_TYPES = {"Concepto", "Localización", "Tiempo", "Localizacion"}


def _normalize_type(t: str) -> str:
    t = (t or "").strip()
    if t.lower() == "localizacion":
        return "Localización"
    return t


def parse_output(model_output: Any) -> List[Dict[str, str]]:
    """
    Procesa y valida las entidades extraídas por el modelo.

    Acepta tanto una lista de dicts como un string (en cuyo caso se devuelve vacío
    para forzar el consumo JSON en los runners).

    Returns:
        list: Lista de entidades válidas y normalizadas con claves 'keyword' y 'type'.
    """
    if not isinstance(model_output, list):
        return []

    allowed = get_entity_types()
    allowed_flat = set(ALLOWED_TYPES)

    cleaned: List[Dict[str, str]] = []
    for item in model_output:
        if not isinstance(item, dict):
            continue
        kw = str(item.get("keyword", "")).strip()
        tp = _normalize_type(str(item.get("type", "")).strip())
        if not kw or not tp:
            continue
        if tp not in allowed_flat:
            continue
        cleaned.append({"keyword": kw, "type": tp})

    return cleaned