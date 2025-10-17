# 🧩 Ejercicio 3: Clasificación de Reclamos

---

## 📝 Descripción

Simulamos ser una **compañía de energía**. Dado un listado de reclamos escritos en lenguaje natural, el sistema debe **clasificar cada reclamo** en una **categoría** y **subcategoría** predefinidas, usando prompts y un modelo de lenguaje (Azure OpenAI).

---

## 📁 Estructura del proyecto

```text
03_CategorizationClaims/
├─ .env                          # Variables de entorno (endpoint, api key, deployment)
├─ README.md                     # Este documento
├─ data/
│  ├─ examples.txt               # Lista de reclamos a clasificar (uno por línea, con viñeta opcional)
│  └─ results/
│     └─ gpt-4-results.json      # Resultados con categoría y subcategoría
├─ models/
│  └─ modelo_4.py                # Script principal de clasificación (AzureOpenAI Chat Completions)
└─ prompts/
   ├─ __init__.py                # Marca el directorio como paquete Python
   ├─ prompt_builder.py          # Construye mensajes (system + user)
   ├─ system_message.py          # Instrucciones y taxonomía (categorías y subcategorías)
   └─ user_message.py            # Formato del mensaje de usuario
```

---

## 🗂️ Taxonomía (Categorías y Subcategorías)

### 💰 Facturación y Cargos

- Errores de facturación.
- Cargos excesivos o no reconocidos.
- Problemas con la lectura del medidor.
- Discrepancias en las tarifas aplicadas.

### ⚡ Calidad del Servicio

- Interrupciones frecuentes del suministro.
- Bajos voltajes o fluctuaciones que dañan los electrodomésticos.
- Problemas con la conexión o reconexión del servicio.

### 🛠️ Instalación y Mantenimiento

- Retrasos o problemas en la instalación de nuevos servicios.
- Falta de mantenimiento adecuado de la infraestructura energética.
- Daños ocasionados por trabajos de instalación o mantenimiento.

### 🔢 Medición y Medidores

- Medidores defectuosos o inexactos.
- Instalación incorrecta de medidores.
- Retrasos en la instalación o reemplazo de medidores.

---

## ⚙️ ¿Cómo funciona?

1. `prompts/system_message.py` define la taxonomía y obliga al modelo a responder en JSON con este formato:

```json
{"categoria": "<Categoría principal>", "subcategoria": "<Subcategoría>"}
```

2. `prompts/user_message.py` inserta el reclamo como texto del usuario.

3. `prompts/prompt_builder.py` arma la lista de mensajes para chat: system + user.

4. `models/modelo_4.py`:

   - Lee `data/examples.txt` (soporta líneas con "- " y comillas).
   - Llama al modelo de Azure OpenAI (Chat Completions) con temperatura 0.
   - Parsea la respuesta JSON; si no es JSON válido, guarda el texto en `raw` como fallback.
   - Imprime progreso por línea: `[idx/total]` con categoría y subcategoría.
   - Escribe los resultados en `data/results/gpt-4-results.json`.

Campos del resultado:

- `input`: línea original del archivo.
- `categoria`: categoría principal detectada.
- `subcategoria`: subcategoría detectada (o `null` si no se pudo extraer).
- `raw`: respuesta original del modelo (para depurar).

---

## 🔧 Configuración

Completa el archivo `.env` con tus credenciales de Azure OpenAI:

- `AZURE_OPENAI_API_KEY_GPT4`
- `AZURE_OPENAI_ENDPOINT_GPT4`
- `OPENAI_MODEL4` (nombre del deployment en Azure)
- `AZURE_API_VERSION` o `AZURE_OPENAI_API_VERSION` (opcional; por defecto `2024-06-01`)

Dependencias (en tu entorno conda):

```powershell
& C:\Users\marta.fraile.jara\AppData\Local\anaconda3\python.exe -m pip install "openai>=1.40.0" "python-dotenv>=1.0.0"
```

---

## ▶️ Ejecución

Opción recomendada (como módulo, evita problemas de imports):

```powershell
cd "c:\Users\marta.fraile.jara\Documents\TrainingExercises\openAI\01_ PromptEngineering\03_CategorizationClaims"
& C:\Users\marta.fraile.jara\AppData\Local\anaconda3\python.exe -m models.modelo_4
```

O bien, pasando el `PYTHONPATH` explícito:

```powershell
$env:PYTHONPATH="c:\Users\marta.fraile.jara\Documents\TrainingExercises\openAI\01_ PromptEngineering\03_CategorizationClaims"
& C:\Users\marta.fraile.jara\AppData\Local\anaconda3\python.exe "c:\Users\marta.fraile.jara\Documents\TrainingExercises\openAI\01_ PromptEngineering\03_CategorizationClaims\models\modelo_4.py"
```

---

## 🗣️ Reclamos de ejemplo

El archivo `data/examples.txt` ya incluye distintos reclamos organizados por categoría. Cada línea puede llevar una viñeta `-` y comillas, y el script las normaliza automáticamente.

---

## 🧪 Consejos y troubleshooting

- Si el modelo devuelve texto en lugar de JSON, se guardará en `raw` y `categoria` tomará ese valor. Revisa el `system_message`.
- Si ves errores de importación, ejecuta como módulo (sección Ejecución) o revisa que `prompts/__init__.py` exista.
- Si hay rate limits, el script reintenta la siguiente línea tras una breve espera.
