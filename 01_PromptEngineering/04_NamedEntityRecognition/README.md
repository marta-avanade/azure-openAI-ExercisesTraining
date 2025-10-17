
 
# 🧩 Ejercicio 4: Named Entity Recognition (NER)

## 🎯 Objetivo

En este ejercicio trabajaremos en el sector bancario y nuestro objetivo es extraer las entidades de una petición de un usuario y clasificarlas en una de las siguientes categorías:

- **Concepto**
- **Localización**
- **Tiempo**

El formato de salida debe ser una lista de diccionarios con la siguiente estructura:

```json
[
  {"keyword": "<keyword 1>", "type": "<type 1>"},
  {"keyword": "<keyword 2>", "type": "<type 2>"},
  ...
]
```

---

## 🧩 Descripción del ejercicio

Dado que esta tarea es más compleja que las anteriores y puede dividirse en pequeñas subtareas, deberás desarrollar el prompt utilizando la técnica paso a paso (step-by-step technique) para guiar al modelo hacia el resultado esperado.

Además, será necesario procesar la salida del prompt para obtener la respuesta final correcta. Para ello, disponemos de una serie de parsers definidos en la carpeta:

`utils/parser`

Deberás utilizar el parser requerido en este caso para validar la salida del modelo.

---

## ⚙️ Valores posibles por tipo de entidad

### 🕒 Tiempo

- `Fecha`

### 💼 Concepto

- `Saldo vivo`
- `Tipo de interés`
- `Tipo de interés medio`
- `Vigencia`
- `Contrato vivo`
- `Importe Concedido`
- `Plazo Concesión`
- `Plazo medio de Concesión`
- `Importe de Nueva formalización`
- `Indicativo de Nueva formalización`
- `Saldo impagado`
- `Importe dudoso`
- `Impago 30+`
- `Impago 90+`
- `Mora temprana`
- `Número de días de impago`
- `Ratio de dudoso`
- `Ratio de impago`
- `Cartera mercado`
- `Producto`
- `Finalidad`
- `Tipo de garantía`
- `Marca Subrogación`
- `Situación morosidad`
- `Tipo de dudoso`
- `Seg. comercial HolaBank`
- `Seg. comercial ImaginBank`
- `Seg. comercial AgroBank`
- `Seg. comercial_feel good`
- `Seg. comercial_food and drinks`
- `Seg. comercial_pharma`
- `Seg. comercial_Real Estate`
- `Seg. comercial_Banca Privada`
- `Tipología de tipo de interés`
- `Marca Cuota Creciente`
- `Marca Ayuda Covid`
- `Indicativo de impago 30+`
- `Indicativo de impago 90+`
- `Contrato en impago`
- `saldo actual, saldo vivo Mercado, riesgo vivo, riesgo total, importe vivo`
- `Tipo interés actual, tipo`
- `Tipo interés actual medio, interés actual, tipo de interés promedio`
- `Operación viva, producto vivo`
- `Capital inicial, importe de concesión, saldo inicial, riesgo inicial`
- `Plazo inicial, plazo de concesión`
- `Plazo inicial medio, plazo de concesión medio, plazo medio de los contratos, plazo medio de cartera`
- `Importe de producción, nuevo importe concedido, riesgo formalizado, nuevo negocio`
- `Nuevo producto, concedido en el mes, nuevo riesgo formalizado, nuevo formalizado`
- `Importe impagado, volumen impagado, saldo de impago, impagado`
- `Importe de mora, Mora contable, NPL, Morosidad contable, stage 3, saldo dudoso`
- `Importe impagado de +30`
- `Importe impagado de +90`
- `Impagados no dudosos, impagados no morosos`
- `Ratio de mora, porcentaje de mora, ratio NPL`
- `porcentaje de impago, porcentajes impagados`
- `Segmentación, cartera`
- `Tipo de activo, tipo de contrato`
- `Motivo de la financiación`
- `Colateral`
- `Situación morosidad, Stage`
- `Cliente de HolaBank`
- `Cliente de Imagin`
- `Cliente de Agro`
- `Cliente feed good`
- `Cliente alimentación y bebidas`
- `Cliente Farma`
- `Cliente de Rela Estate, mercado inmobiliario`
- `Cliente de Banca Privada`
- `Amortización creciente`
- `Contrato impagado`

### 📍 Localización

- `DT del contrato`
- `DG del contrato`
- `DAN del contrato`
- `Oficina del contrato`
- `Provincia del contrato`
- `Comunidad autónoma`
- `Población del contrato`
- `Empresa origen`
- `Dirección Territorial`
- `Dirección Comercial`
- `Dirección Área de Negocio, Dirección de Zona`
- `Centro de empresa, Store`
- `Prov.`
- `CA, Com.Aut. CCAA`
- `Ciudad, pueblo, localidad`
- `Entidad de origen`

---

## 🧠 Ejemplos de entradas y salidas esperadas

| Entrada | Salida esperada |
|---------|-----------------|
| ¿Cuál es el saldo vivo por Dirección Territorial en septiembre de 2023? | `[{"keyword": "saldo vivo", "type": "Concepto"}, {"keyword": "Dirección Territorial", "type": "Localizacion"}, {"keyword": "septiembre de 2023", "type": "Tiempo"}]` |
| ¿Qué Dirección Territorial ha disminuido más el dudoso en el año? | `[{"keyword": "Dirección Territorial", "type": "Localizacion"}, {"keyword": "dudoso", "type": "Concepto"}, {"keyword": "el año", "type": "Tiempo"}]` |
| ¿Cuál es el saldo dudoso, del último mes en la DAN de madrid? | `[{"keyword": "saldo dudoso", "type": "Concepto"}, {"keyword": "ultimo mes", "type": "Tiempo"}, {"keyword": "DAN de madrid", "type": "Localizacion"}]` |
| Dime la producción de autónomos distribuido por tipo de interés | `[{"keyword": "producción de autónomos", "type": "Concepto"}, {"keyword": "por tipo de interés", "type": "Concepto"}]` |
| ¿Cuál es el ratio de mora de Andalucía? | `[{"keyword": "ratio de mora", "type": "Concepto"}, {"keyword": "Andalucía", "type": "Localizacion"}]` |
| ¿Cuál es el porcentaje de impagos en junio? | `[{"keyword": "porcentaje de impagos", "type": "Concepto"}, {"keyword": "junio", "type": "Tiempo"}]` |
| ¿Cuál es la evolución de nuevos productos por Dirección Territorial en 2023? | `[{"keyword": "nuevos productos", "type": "Concepto"}, {"keyword": "Dirección Territorial", "type": "Localizacion"}, {"keyword": "2023", "type": "Tiempo"}]` |
| ¿Quién ha formalizado más préstamos en enero del 2023 Madrid o Barcelona? | `[{"keyword": "prestamos", "type": "Concepto"}, {"keyword": "enero del 2023", "type": "Tiempo"}, {"keyword": "Madrid", "type": "Localizacion"}, {"keyword": "Barcelona", "type": "Localizacion"}]` |

---

## 🗂️ Estructura de carpetas (final)

```text
04_NamedEntityRecognition/
│
├── data/
│   ├── input_data.json            # Frases de entrada a procesar (array "examples")
│   ├── output_data_gpt-35-turbo.json  # Salida estructurada (se genera al ejecutar gpt35)
│   └── output_data_gpt-4.json         # Salida estructurada (se genera al ejecutar gpt4)
│
├── models/
│   ├── gpt35_runner.py            # Ejecuta GPT-35 (Azure) con tool-calling; imprime y guarda resultados
│   └── gpt4_runner.py             # Ejecuta GPT-4 (Azure) con tool-calling; imprime y guarda resultados
│
├── prompts/
│   ├── prompt_builder.py          # Une system + user + texto de entrada
│   ├── system_message.py          # Mensaje del sistema (exige salida JSON estricta)
│   └── user_message.py            # Mensaje del usuario (instrucciones y formato de salida)
│
├── utils/
│   ├── entity_types.py            # Taxonomía de tipos/valores admitidos
│   └── parser.py                  # Normaliza/valida la salida del modelo
│
├── .env                           # Claves y configuración de Azure OpenAI
└── README.md
```

---

## ⚙️ Cómo funciona el programa (claro y visual)

1. Carga de configuración

- Se lee `.env` para obtener: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT y AZURE_OPENAI_API_VERSION.

1. Entrada

- Se leen las frases desde `data/input_data.json` en la clave `examples`.

1. Construcción de prompt

- `prompts/prompt_builder.py` combina `system_message` + `user_message` + el texto de la frase.

1. Llamada al modelo con tool-calling (salida JSON garantizada)

- Los runners (`gpt35_runner.py` y `gpt4_runner.py`) usan Azure OpenAI con una herramienta (function) `return_entities` que define el esquema: lista de objetos `{keyword, type}`.
- Se fuerza al modelo a usar esa función, priorizando una salida estrictamente JSON.

1. Normalización y validación

- La salida se valida con `utils/parser.py` para asegurar tipos válidos y campos completos.
- Si el modelo devolviera texto en viñetas, existe un fallback heurístico que lo convierte a JSON.

1. Salida por consola (formato exacto)

- Por cada frase, se imprime una fila Markdown con el JSON entre backticks:

  | ¿Quién ha formalizado más préstamos en enero del 2023 Madrid o Barcelona? | `[{"keyword": "prestamos", "type": "Concepto"}, {"keyword": "enero del 2023", "type": "Tiempo"}, {"keyword": "Madrid", "type": "Localizacion"}, {"keyword": "Barcelona", "type": "Localizacion"}]` |

1. Archivo de resultados (estructurado)

- Se genera un JSON con metadatos y resultados:
  - `data/output_data_gpt-35-turbo.json` al ejecutar GPT-35.
  - `data/output_data_gpt-4.json` al ejecutar GPT-4.
- Contenido (resumen):
  - `model`, `endpoint`, `api_version`, `generated_at`, `input_summary.total`.
  - `results[]`: para cada `input`, se guarda `output.raw_text`, `output.parsed` (lista validada) y `output.origin` (tool_call / model_json / heuristic).

---

## 🧰 Ejecución del ejercicio

### Instrucciones

1. Sigue la checklist de Prompt Engineering.
2. Divide la tarea en pasos lógicos y claros.
3. Configura `.env` con tu Azure OpenAI.
4. Ejecuta `models/gpt35_runner.py` para procesar todas las frases de `data/input_data.json` y generar `output_data_gpt-35-turbo.json`.
5. Ejecuta `models/gpt4_runner.py` para generar `output_data_gpt-4.json` con el mismo formato.
6. Revisa la consola: verás una fila por cada frase con el JSON entre backticks.
7. Revisa los archivos de salida en `data/` para auditoría y consumo posterior.

---

## 💡 Hints (pistas útiles)

- Cuando pruebes con **gpt-35-turbo**, notarás que algunos conceptos como “Evolución” pueden ser clasificados como Concepto.
- Si intentas resolverlo diciendo que “no es un concepto”, verás que es complicado.

### ➜ Buena práctica

Define una nueva categoría llamada **“Analysis”** para este tipo de palabras (evolución, tendencia, mayor, menor, etc.). Así, mediante una función Python posterior, podrás procesarlas y eliminar las que estén clasificadas como “Analysis” para quedarte solo con las entidades realmente relevantes.

#### Ejemplo

```python
resultados = [
  {"keyword": "saldo vivo", "type": "Concepto"},
  {"keyword": "evolución", "type": "Analysis"}
 }


filtrados = [r for r in resultados if r["type"] != "Analysis"]
```
