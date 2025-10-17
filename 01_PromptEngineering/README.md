# 🧠 Tema: Prompt Engineering

## 📘 Objetivo general

Aprender a escribir prompts correctamente y entender cómo “piensan” los modelos de lenguaje (como los de OpenAI). Durante esta sección vas a practicar cómo redactar prompts para distintas tareas, usando buenas prácticas, checklists y comparando resultados entre modelos (gpt-3.5 y gpt-4).

---

## ⚙️ Contexto

OpenAI publica constantemente nuevos modelos y versiones (GPT-3.5, GPT-4, GPT-4-Turbo, etc.).

Cada modelo funciona de manera diferente, por eso es importante seguir siempre las buenas prácticas oficiales.

En los ejercicios usarás código del Prompt Engineering Accelerator, que te permite enviar prompts a los modelos de OpenAI.
👉 Lo difícil no es el código, sino diseñar un buen prompt.

---

## 📋 Checklist (resumen general para todos los ejercicios)

En cada ejercicio tendrás que:

1. Seguir el Prompt Engineering Checklist (buenas prácticas para redactar prompts).
2. Definir el `system_message` (instrucciones al modelo).
3. Definir el `user_message` (el texto o la consulta del usuario).
4. Usar el parser correspondiente (una función que procesa la salida del modelo).
5. Probar varias frases o ejemplos.
6. Identificar las dificultades y analizar cómo responde cada modelo.
7. Comparar resultados entre `gpt-3.5-turbo` y `gpt-4` / `gpt-4-turbo`.

---

## 🧩 Ejercicio 1: Dates Extractor (Extractor de Fechas)

### 🎯 Objetivo del Ejercicio 1

Extraer todas las fechas que aparezcan en un texto y devolverlas en formato “dd/mm/yyyy”.

### 🧠 Pasos a Seguir en el Ejercicio 1

1. Crear un prompt que le diga al modelo que:
   - Lea un texto.
   - Encuentre todas las fechas (sin importar cómo estén escritas: “2023-04-15”, “10/15/2023”, “23 de octubre de 2023”, etc.).
   - Devuelva un listado de fechas en formato `dd/mm/yyyy`.
2. Probar con los textos que te dan (hay 5 ejemplos con distintas formas de escribir fechas).
3. Usar el parser de fechas (que está en la carpeta `utils/parser`).
4. Analizar las dificultades (por ejemplo, formatos distintos o fechas con palabras).
5. Comparar resultados entre `gpt-3.5-turbo` y `gpt-4` y ver las diferencias.

💡 **Sugerencia**

En el `user_prompt`, indica claramente el formato de salida. Ejemplo:

```python
user_prompt = f"""{user_input}

Response:
[
"""
```

---

## 🧩 Ejercicio 2: Intent Classification (Clasificación de Intenciones)

### 🎯 Objetivo del Ejercicio 2

Simular un bot bancario que clasifica la intención del usuario en una de las siguientes categorías:

- **Balance inquiry** – Consultas de saldo.
- **Card management** – Gestión de tarjetas.
- **Opening accounts or signing up for products** – Apertura de cuentas o contratación de productos.
- **Help & Support** – Soporte técnico y ayuda.
- **Other** – Si no pertenece a ninguna de las anteriores.

### 🧠 Pasos a Seguir en el Ejercicio 2

1. Crear un prompt que clasifique la intención del usuario.
2. Probar con las frases dadas (en cada categoría hay 5 ejemplos).
3. Incluir frases que no pertenezcan a ninguna categoría (para comprobar que el modelo responde “Other”).
4. Usar el parser correspondiente para procesar la salida.
5. Comparar resultados.

🔧 **Modelo**

Usa `gpt-4-turbo`.

---

## 🧩 Ejercicio 3: Categorization of Claims (Clasificación de Reclamos de Energía)

### 🎯 Objetivo del Ejercicio 3

Simular un bot de una compañía eléctrica que clasifica reclamos de clientes en 4 categorías:

- **Billing and Charges** – Facturación y cobros.
- **Quality of Service** – Calidad del servicio.
- **Installation and Maintenance** – Instalación y mantenimiento.
- **Metering and Meters** – Medición y contadores.

### 🧠 Pasos a Seguir en el Ejercicio 3

1. Crear el prompt que clasifica cada reclamo en una categoría.
2. Usar el parser correspondiente.
3. Probar con las frases dadas (5 por categoría).
4. Usar `gpt-4-turbo`.

💬 **Observación**

Cambiando solo la “base de conocimiento” (es decir, las categorías), puedes generalizar el prompt y crear clasificadores para otros sectores o dominios.

---

## 🧩 Ejercicio 4: Named Entity Recognition (Reconocimiento de Entidades Nombradas - NER)

### 🎯 Objetivo del Ejercicio 4

En el sector bancario, extraer entidades de una pregunta del usuario y clasificarlas en:

- **Concepto**
- **Localización**
- **Tiempo**

### 🧱 Formato de salida requerido

```json
[
 {"keyword": "<palabra o frase>", "type": "<tipo>"},
 {"keyword": "<palabra o frase>", "type": "<tipo>"},
 ...
]
```

### 🧠 Pasos a Seguir en el Ejercicio 4

1. Usar el modelo `gpt-4-turbo`.
2. Crear el `system_message` con la técnica paso a paso (step-by-step) para que el modelo razone antes de responder.
3. Crear el `user_message` (la pregunta).
4. Probar con las frases de ejemplo.
5. Usar el parser correspondiente.
6. Repetir todo con `gpt-3.5-turbo` y comparar resultados.

💡 **Sugerencia importante**

Algunos modelos (como `gpt-3.5`) tienden a clasificar palabras como “evolución” o “tendencia” como **Concepto**, cuando en realidad no lo son.

En lugar de decirle “esto no es un concepto”, añade una nueva categoría, por ejemplo ‘Analysis’, y luego la filtras con código Python para quedarte solo con **Concepto/Localización/Tiempo**.
