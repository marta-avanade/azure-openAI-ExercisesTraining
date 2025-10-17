# 🧠 Ejercicio: Embedding & Q&A

## 🎯 Objetivo general

Implementar un sistema de preguntas y respuestas (Q&A) sobre un documento en formato PDF, aplicando técnicas de embeddings para representar el texto y permitir que el modelo entienda y responda de forma precisa según el contenido del documento.

---

## 🧩 Instrucciones del ejercicio

Sigue los pasos de esta checklist de manera simultánea junto con las indicaciones detalladas a continuación. Recuerda aplicar buenas prácticas en el uso de repositorios y la ejecución del código.

### 1️⃣ Preparación del JSON del PDF

- Convierte el PDF en un archivo JSON que contenga su estructura textual.
- Asegúrate de que el formato sea legible y que incluya correctamente los capítulos y secciones.
- Este JSON será la base para crear los embeddings.

### 2️⃣ Selección de capítulos

- Selecciona solo 3 capítulos del PDF y añádelos en la variable `section_list` dentro del archivo `config.py`.
- Es muy importante que los títulos que incluyas en `section_list` coincidan exactamente con los títulos de los capítulos tal y como aparecen en el PDF.
- Si hay diferencias (por ejemplo, mayúsculas, espacios o puntuación), el sistema no podrá leerlos correctamente.
- Revisa cuidadosamente el archivo JSON para asegurarte de que se está identificando la sección correcta.

### 3️⃣ Adición manual de un capítulo

- Añade un capítulo adicional manualmente en el archivo `.jsonl`.
- Este paso tiene como propósito recordarte que el proceso `pdf_to_json` no siempre es completamente automático.
- En algunos casos, será necesario añadir o corregir información manualmente en el archivo resultante.

### 4️⃣ Creación y verificación de embeddings

- Una vez preparado el JSON con las secciones adecuadas, genera los embeddings correspondientes.
- Verifica que se hayan creado correctamente y que los datos representen fielmente el contenido de las secciones seleccionadas.

### 5️⃣ Pruebas del chat Q&A

- Realiza una fase de prueba haciendo al chat un conjunto de preguntas:
  1. 5 preguntas básicas, relacionadas con información directa o sencilla del documento.
  2. 5 preguntas complejas, que requieran inferencia, relación entre secciones o comprensión contextual.
- Comprueba si las respuestas del modelo son correctas, coherentes y precisas según el contenido del PDF.

### 6️⃣ Iteración de la solución

- Si durante las pruebas anteriores no obtienes los resultados esperados, analiza posibles mejoras en el proceso:
  - ¿Podría mejorarse la selección de secciones?
  - ¿Es necesario limpiar o reestructurar el texto del PDF?
  - ¿Podría beneficiarse el sistema de un ajuste en los parámetros del modelo o del proceso de embeddings?
- Reflexiona sobre cómo iterar la solución para que el chat responda de forma más precisa y útil.

---

## 🧭 Resultado esperado

Al finalizar el ejercicio, deberías tener:

- Un archivo JSON correctamente estructurado con las secciones seleccionadas.
- Un conjunto de embeddings creados y verificados.
- Un chat funcional capaz de responder preguntas sobre el PDF.

---

# 🧠 REALIZACION DEL PROYECTO

Este README describe la estructura del proyecto, qué hace cada script dentro de `02_Embedding`, cómo ejecutar el pipeline, ejemplos de `.env` y una sección TODO con pasos recomendados.

## Estructura del proyecto (resumen)

```
02_Embedding/
├─ .env                      # Variables de entorno (no versionar en repos públicos)
├─ config.py                 # Lista de títulos (section_list) y ajustes
├─ requirements.txt
├─ DocumentIntelligence/
│  └─ scripts/
│     └─ pdf_to_json.py      # Llamadas a Azure DI -> DocumentIntelligence/data/output.json
├─ data/
│  ├─ sections/              # -> sections.jsonl
│  ├─ embeddings/            # -> embeddings.jsonl
│  ├─ logs/                  # -> qa_runs.jsonl
│  ├─ candidate_sections.json
│  ├─ questions.txt
│  └─ manual_chapter.txt
└─ scripts/
   ├─ 01_list_candidate_sections.py
   ├─ 02_validate_section_list.py
   ├─ 02b_debug_find_titles.py
   ├─ 03_slice_sections.py
   ├─ 04_add_manual_chapter.py
   ├─ 05_create_embeddings.py
   └─ 06_rag_qa.py
```

## Qué hace cada script (detallado)

- `DocumentIntelligence/scripts/pdf_to_json.py`
  - Llama a Azure Document Intelligence (prebuilt-layout) para analizar un PDF.
  - Simplifica el resultado a un JSON con páginas y texto (`pages: [{page_number, text}]`).
  - Salida por defecto: `02_Embedding/DocumentIntelligence/data/output.json`. Puedes sobreescribir con `EMBEDDING_SOURCE_JSON`.

- `scripts/01_list_candidate_sections.py`
  - Escanea `output.json` y extrae líneas que parezcan títulos (heurística).
  - Guarda `data/candidate_sections.json` para revisar y elegir títulos exactos.

- `scripts/02_validate_section_list.py`
  - Comprueba que los títulos en `config.section_list` aparecen exactamente en el `output.json`.
  - Imprime sugerencias cercanas en caso de no encontrar coincidencias exactas.

- `scripts/02b_debug_find_titles.py`
  - Herramienta de diagnóstico para localizar en qué página aparece cada título y si la ocurrencia está dentro del ToC.
  - Útil para ajustar `section_list` cuando el ToC confunde la detección.

- `scripts/03_slice_sections.py`
  - Toma el `output.json` y los 3 títulos en `config.section_list`, localiza su primera aparición (evitando ToC) y crea `data/sections/sections.jsonl`.
  - Formato: JSONL con campos {id, title, start_page, end_page, content}.

- `scripts/04_add_manual_chapter.py`
  - Añade un capítulo manual al `sections.jsonl` (toma `data/manual_chapter.txt` por defecto o `--text-file`).

- `scripts/05_create_embeddings.py`
  - Lee `data/sections/sections.jsonl`, lanza la API de embeddings (Azure OpenAI) y escribe `data/embeddings/embeddings.jsonl`.
  - Registra advertencias si el contenido está vacío y escribe vectores (o `[]` en caso de error) por cada sección.

- `scripts/06_rag_qa.py`
  - Flujo RAG: calcula embedding de la consulta, recupera top-k por similitud coseno desde `embeddings.jsonl`, construye prompt con las secciones relevantes y consulta el despliegue de chat.
  - Guarda cada run en `data/logs/qa_runs.jsonl` con metadatos (ts, pregunta, indices, scores, titles, answer).

## Variables .env (ejemplo)

Copia este bloque en `02_Embedding/.env` y completa con tus valores:

```ini
# Azure Document Intelligence
AZURE_ENDPOINT=https://<tu-azure-di-resource>
AZURE_API_KEY=<tu-di-key>
AZURE_API_VERSION=2023-07-31
AZURE_MODEL_ID=prebuilt-layout

# Azure OpenAI (embeddings + chat completions)
AZURE_OPENAI_ENDPOINT=https://<tu-openai-endpoint>
AZURE_OPENAI_API_KEY=<tu-openai-key>
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini

# Overrides de rutas (opcionales)
EMBEDDING_SOURCE_JSON=./02_Embedding/DocumentIntelligence/data/output.json
SECTIONS_JSONL_PATH=./02_Embedding/data/sections/sections.jsonl
EMBEDDINGS_JSONL_PATH=./02_Embedding/data/embeddings/embeddings.jsonl
QA_RUNS_JSONL_PATH=./02_Embedding/data/logs/qa_runs.jsonl
```

Nota: guarda el archivo pero no subas tus keys a repositorios públicos.

## Flujo rápido (comandos útiles)

- Generar JSON desde PDF (Azure DI):

```powershell
python .\02_Embedding\DocumentIntelligence\scripts\pdf_to_json.py
```

- Revisar candidatos:

```powershell
python .\02_Embedding\scripts\01_list_candidate_sections.py
```

- Validar títulos y ajustar `config.py`:

```powershell
python .\02_Embedding\scripts\02_validate_section_list.py
```

- Slice en secciones y generar `sections.jsonl`:

```powershell
python .\02_Embedding\scripts\03_slice_sections.py
```

- Añadir capítulo manual (opcional):

```powershell
python .\02_Embedding\scripts\04_add_manual_chapter.py --text-file .\02_Embedding\data\manual_chapter.txt
```

- Crear embeddings (requiere `.env` con deploy correcto):

```powershell
python .\02_Embedding\scripts\05_create_embeddings.py
```

- Ejecutar RAG Q&A:

```powershell
python .\02_Embedding\scripts\06_rag_qa.py -q "¿Cuál es el propósito de la política de gastos?" -k 3
```

## Troubleshooting rápido

- Embeddings vacíos:
  - Comprueba `AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT` y que la clave/endpoint sean correctos en `.env`.
  - Ejecuta `05_create_embeddings.py` desde el entorno Python donde instalaste `requirements.txt`.

- Títulos no encontrados:
  - Ejecuta `02b_debug_find_titles.py` para localizar si la coincidencia aparece solo en el ToC o en páginas posteriores.

- Chat no devuelve respuesta útil:
  - Asegúrate de que `AZURE_OPENAI_CHAT_DEPLOYMENT` esté definido y que el modelo tenga acceso en tu recurso.
  - Reduce `temperature` en `06_rag_qa.py` o ajusta `max_tokens`.
