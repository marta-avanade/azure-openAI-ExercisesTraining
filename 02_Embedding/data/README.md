Estructura recomendada de la carpeta data/:
## Estructura organizada de `data/`

Este directorio contiene los artefactos intermedios y finales usados por los scripts del ejercicio **02_Embedding**.

Árbol recomendado:

```
data/
├─ sections/
│  └─ sections.jsonl       # Salida de `03_slice_sections.py` y `04_add_manual_chapter.py`
├─ embeddings/
│  └─ embeddings.jsonl     # Salida de `05_create_embeddings.py` (vectores JSONL)
├─ logs/
│  └─ qa_runs.jsonl        # Historial de preguntas/respuestas generado por `06_rag_qa.py`
├─ candidate_sections.json # Resultado de `01_list_candidate_sections.py` (títulos detectados)
├─ questions.txt           # 5 básicas + 5 difíciles (archivo de ejemplo)
└─ manual_chapter.txt      # Texto fuente para `04_add_manual_chapter.py`
```