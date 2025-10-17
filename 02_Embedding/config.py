# Configuración del ejercicio de Embeddings (Paso 2: selección de capítulos)
#
# Rellena "section_list" con EXACTAMENTE los títulos de 3 capítulos
# tal y como aparecen en el JSON generado por Document Intelligence.
# Puedes usar los scripts en 02_Embedding/scripts para ayudarte a detectar
# candidatos y validar coincidencias.

# Ejemplo (sustituye por tus títulos exactos):
# section_list = [
#     "Capítulo 1. Introducción",
#     "Capítulo 2. Metodología",
#     "Capítulo 3. Resultados"
# ]

section_list: list[str] = [
    "I. Overview",
    "II. Time and Expense Reporting",
    "III. Time/Expense Report Submission",
]


def get_section_list() -> list[str]:
    """Devuelve la lista de secciones seleccionadas (3 títulos exactos)."""
    return section_list
