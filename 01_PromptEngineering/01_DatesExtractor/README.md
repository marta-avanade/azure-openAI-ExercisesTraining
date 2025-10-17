# 🧩 Ejercicio 1: Dates Extractor

## 🎯 Objetivo

Extraer todas las fechas que aparezcan en un texto y devolverlas en formato `dd/mm/yyyy`.

---

## 🧠 Paso 1. Analiza el problema

El modelo debe:

1. Leer un texto (que puede tener fechas escritas de distintas formas).
2. Detectar todas las fechas.
3. Ignorar las horas (“14:30”, “09:00 AM”, etc.).
4. Devolverlas todas en el formato `dd/mm/yyyy`.

---

## ⚙️ Paso 2. Define los mensajes del prompt

### 🧾 System Message

Este mensaje le da contexto general al modelo (su “rol”).
Ejemplo recomendado:

```python
system_message = """
Eres un asistente especializado en extracción de información. 
Tu tarea es identificar todas las fechas mencionadas en un texto 
y devolverlas exclusivamente en formato 'dd/mm/yyyy'. 
Ignora horas y cualquier otra información no relacionada con fechas.
Devuelve la respuesta en formato de lista Python, así:

[
 "dd/mm/yyyy",
 "dd/mm/yyyy",
 ...
]
"""
```

### 💬 User Message

El mensaje del usuario contendrá el texto del que se quieren extraer las fechas.
Ejemplo:

```python
user_message = """
La conferencia de tecnología se llevará a cabo el 2023-04-15 en el centro de convenciones de la ciudad.
"""
```

---

## 🧮 Paso 3. Especifica el formato de salida (muy importante)

Una buena práctica es incluir en el prompt cómo debe empezar la respuesta, para que el modelo devuelva una lista limpia y fácil de procesar:

```python
user_prompt = f"""
{user_input}

Respuesta esperada:
[
"""
```

Esto ayuda a que el modelo no incluya texto adicional ni explicaciones.

---

## 🧩 Paso 4. Textos para probar

Debes probar con los siguientes casos (usa uno por uno):

1️⃣

"La conferencia de tecnología se llevará a cabo el 2023-04-15 en el centro de convenciones de la ciudad."

2️⃣

"La temporada cultural de otoño arranca con una serie de eventos imperdibles. El primero será la exposición de arte moderno que abre sus puertas el 10/15/2023 en el Museo de la Ciudad. A continuación, el 23 de octubre de 2023, se presentará la obra 'Luces de Bohemia' en el Teatro Principal. Finalmente, no te pierdas la feria del libro que se realizará del 11-01-2023 al 11-05-2023."

3️⃣

"El proyecto de desarrollo de software se desglosa en varias fases clave con fechas de entrega específicas. La fase de investigación debe completarse antes del 2023-05-20. La etapa de diseño y prototipado está programada para el período comprendido entre el 01/06/2023 y el 31/07/2023. La implementación del código comenzará el 1 de agosto de 2023 y se extenderá hasta el 30 de septiembre de 2023. Por último, la fase de pruebas y ajustes se llevará a cabo del 10-10-2023 al 10-12-2023, asegurando que el producto final esté listo para su lanzamiento el 15 de diciembre de 2023."

4️⃣

"El vuelo está programado para despegar a las 14:30 del 05-06-2023 desde el aeropuerto internacional."

5️⃣

"La videoconferencia internacional se iniciará a las 09:00 AM GMT del 22 de noviembre de 2023."

---

## 🧰 Paso 5. Usa el parser correspondiente

El proyecto menciona que existen parsers en la carpeta `utils/parser`.
En este caso, usarías el parser de fechas, que probablemente:

1. Recibe la salida del modelo.
2. Limpia texto adicional.
3. Convierte las fechas a objetos `datetime` o strings uniformes (`dd/mm/yyyy`).

(En esta etapa solo asegúrate de que tu salida sea consistente y fácil de procesar por el parser.)

---

## 🧪 Paso 6. Prueba con diferentes modelos

### 🔹 Modelo 1: gpt-3.5-turbo

- Puede tener más errores con formatos poco comunes o fechas escritas con palabras (“23 de octubre de 2023”).
- Es menos consistente en mantener el formato solicitado.

### 🔹 Modelo 2: gpt-4

- Suele detectar mejor fechas expresadas con palabras.
- Tiende a mantener el formato correcto.

👉 Tu tarea es comparar los resultados y anotar:

- ¿Qué fechas omite o malinterpreta cada modelo?
- ¿Cuál respeta mejor el formato `dd/mm/yyyy`?

---

## 🧩 Paso 7. Documenta las dificultades

Algunos problemas comunes que deberás observar:

- Fechas escritas con mes en palabras (“octubre”, “noviembre”).
- Fechas con rangos (“del 11-01-2023 al 11-05-2023”).
- Fechas incompletas o con día en texto (“1 de agosto de 2023”).
- Confusión con horas o zonas horarias (el modelo podría intentar extraerlas como fechas).

---

## ⚙️ Cómo funciona este ejercicio (visión general)

Flujo de punta a punta:

1. Los textos de prueba están en `text_examples/*.txt`.
2. `prompts/prompts.py` construye:
   - `system_message`: instrucciones para extraer fechas en formato `dd/mm/yyyy`.
   - `user_messages`: se cargan automáticamente desde `text_examples`.
3. `models/modelo_35.py` y `models/modelo_4.py` leen el `.env`, envían los prompts a Azure OpenAI (deployments GPT‑3.5 y GPT‑4) y guardan las respuestas en `results/{modelo}.json`.
4. `comparar_resultados.py` lee ambos JSON y resume similitudes/diferencias.

---

## 🗂️ Estructura de carpetas

```text
01_DatesExtractor/
├─ text_examples/           # Casos de prueba (txt)
├─ prompts/
│  └─ prompts.py            # system_message + carga de user_messages
├─ models/
│  ├─ modelo_35.py          # Ejecuta GPT‑3.5 (deployment gpt‑35)
│  └─ modelo_4.py           # Ejecuta GPT‑4 (deployment gpt‑4)
├─ utils/
│  └─ parser.py             # (opcional) utilidades para formatear/validar fechas
├─ results/                 # Salidas en JSON por modelo
├─ comparar_resultados.py   # Compara los resultados 3.5 vs 4
└─ .env                     # Variables de entorno (claves, endpoints, deployments)
```

---

## 🔐 Variables de entorno (.env)

Variables generales (fallback):

- `AZURE_OPENAI_API_KEY`: clave del recurso Azure OpenAI
- `AZURE_OPENAI_ENDPOINT`: url del recurso (por ejemplo: <https://mi-recurso.openai.azure.com/>)
- `AZURE_API_VERSION`: versión API (p. ej. 2025-01-01-preview)
- `OPENAI_MODEL`: nombre del deployment por defecto (p. ej. gpt-35-turbo)

Variables específicas por modelo (si existen, tienen prioridad):

- GPT‑3.5
  - `OPENAI_MODEL35` (p. ej. gpt-3.5-turbo o gpt-35-turbo según tu deployment)
  - `AZURE_OPENAI_API_KEY_GPT35`
  - `AZURE_OPENAI_ENDPOINT_GPT35`

- GPT‑4
  - `OPENAI_MODEL4` (p. ej. gpt-4)
  - `AZURE_OPENAI_API_KEY_GPT4`
  - `AZURE_OPENAI_ENDPOINT_GPT4`

Los scripts usan primero las variables específicas y, si no están, caen a las generales.

---

## 📦 Requisitos

- Python 3.9+ (recomendado)
- Paquetes Python: `openai`, `python-dotenv`

---

## ▶️ Cómo ejecutar

Instalar dependencias (una vez):

```powershell
pip install openai python-dotenv
```

Ejecutar el modelo GPT‑3.5 (guardará `results/gpt-35-turbo.json`, o el nombre que definas):

```powershell
python ".\01_ PromptEngineering\01_DatesExtractor\models\modelo_35.py"
```

Ejecutar el modelo GPT‑4 (guardará `results/gpt-4.json`, o el nombre que definas):

```powershell
python ".\01_ PromptEngineering\01_DatesExtractor\models\modelo_4.py"
```

Comparar resultados (muestra un resumen en consola):

```powershell
python ".\01_ PromptEngineering\01_DatesExtractor\comparar_resultados.py"
```

---

## 📁 Salidas esperadas

- `results/gpt-35-turbo.json` (o el deployment configurado) con objetos `{ "input": str, "output": str }`.
- `results/gpt-4.json` (o el deployment configurado) con el mismo formato.
- Resumen de comparación por consola indicando:
  - Fechas comunes a ambos modelos.
  - Fechas solo halladas por GPT‑3.5 o solo por GPT‑4.
  - Diferencias por cada caso de prueba.

---

## 📝 Notas

- Si tu deployment en Azure tiene otro nombre, cambia `OPENAI_MODEL35` / `OPENAI_MODEL4` en el `.env`.
- Si obtienes errores de autenticación, revisa las claves y el endpoint en el `.env`.
- Puedes añadir un parser en `utils/parser.py` para normalizar aún más las salidas antes de comparar (por ejemplo, forzar `dd/mm/yyyy`).