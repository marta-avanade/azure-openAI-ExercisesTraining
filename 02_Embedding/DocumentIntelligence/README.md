# Document Intelligence: PDF a JSON

Convierte un PDF en JSON usando Azure Document Intelligence (Form Recognizer).

## Requisitos

- Variables en `.env` (en `02_Embedding/DocumentIntelligence/.env`):
  - `PDF_INPUT_PATH` (por defecto `./data/input.pdf`)
  - `JSON_OUTPUT_PATH` (por defecto `./data/output.json`)
  - `AZURE_ENDPOINT` (tu endpoint de Azure DI)
  - `AZURE_API_KEY` (tu API key)
  - Opcional: `AZURE_API_VERSION` (por defecto `2023-07-31`), `AZURE_MODEL_ID` (por defecto `prebuilt-layout`)
  - Opcional: `RAW_JSON_OUTPUT_PATH` (si lo defines, también se guardará la respuesta cruda del servicio)

## Ejecutar

Desde `02_Embedding/DocumentIntelligence/` o cualquier ruta (el script resuelve paths relativos):

```powershell
python scripts/pdf_to_json.py
```

El resultado se guarda en `JSON_OUTPUT_PATH`.

### ¿Qué se guarda en `JSON_OUTPUT_PATH`?

Se guarda un JSON simplificado pensado para el ejercicio de embeddings, con el texto por página:

```json
{
  "pages": [
    { "page_number": 1, "text": "Texto de la página 1..." },
    { "page_number": 2, "text": "Texto de la página 2..." }
  ]
}
```

Reglas de extracción:

- Prioriza párrafos por página (`paragraphs` + `boundingRegions`).
- Si no hay párrafos, usa líneas por página (`pages[].lines[].content`).
- Si no hay líneas, usa `analyzeResult.content` como fallback.

Si defines `RAW_JSON_OUTPUT_PATH`, además se guarda el JSON completo retornado por Azure (útil para auditoría y debugging).

## Solución de problemas

- “Input PDF not found”: revisa `PDF_INPUT_PATH` en `.env` o usa una ruta absoluta.
- Archivo de salida termina en `.pdf`: asegúrate de que `JSON_OUTPUT_PATH` termine en `.json` (el script ya lo corrige automáticamente y avisa).
- 401/403: valida `AZURE_ENDPOINT` y `AZURE_API_KEY`.
- Tiempo de espera: puedes ajustar `AZURE_API_VERSION`/`AZURE_MODEL_ID`; si tarda demasiado, el script hace polling con timeout.
