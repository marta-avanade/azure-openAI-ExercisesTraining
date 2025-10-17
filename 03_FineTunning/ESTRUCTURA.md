# 📁 Estructura del Proyecto

```
03_FineTunning/
├── 📄 README.md                    # Documentación principal
├── 📄 requirements.txt             # Dependencias Python
├── 📄 run_all_steps.py             # Script para ejecutar todo el proceso
├── 📄 .env                         # Variables de entorno (configuración Azure)
│
├── 📂 config/
│   └── 📄 config.py                # Configuración del proyecto
│
├── 📂 data/
│   ├── 📂 raw/                     # Datos originales (JSON de ejemplos)
│   ├── 📂 processed/               # Datos procesados (prompts JSONL)
│   ├── 📂 training/                # Datos de entrenamiento
│   └── 📂 validation/              # Datos de validación
│
├── 📂 scripts/
│   ├── 📄 01_create_examples.py    # Crear ejemplos de intenciones
│   ├── 📄 02_create_prompts.py     # Generar prompts para entrenamiento
│   ├── 📄 03_split_data.py         # Dividir datos train/validation
│   ├── 📄 04_prepare_data.py       # Preparar datos para fine-tuning
│   ├── 📄 05_fine_tuning.py        # Ejecutar fine-tuning en Azure
│   ├── 📄 06_deploy_model.py       # Desplegar modelo
│   ├── 📄 07_test_model.py         # Probar modelo con casos de prueba
│   └── 📄 08_analyze_results.py    # Analizar resultados y mejoras
│
├── 📂 models/                      # Información de modelos (futuro)
├── 📂 results/                     # Resultados, reportes y métricas
├── 📂 tests/                       # Casos de prueba adicionales
└── 📂 logs/                        # Logs del proceso
```

## � Descripción Detallada de Scripts

### 🔸 **01_create_examples.py** - Crear Ejemplos de Intenciones
**Propósito**: Genera el dataset inicial con ejemplos de texto para cada intención de la tienda.

**Qué hace**:
- Crea 48 ejemplos (12 por cada intención): `comprar`, `devolver`, `queja`, `consulta`
- Cada ejemplo es una frase realista que un cliente diría en una tienda de ropa
- Guarda los datos en formato JSON en `data/raw/intent_examples.json`
- Valida que todas las intenciones tengan suficientes ejemplos (mín. 10 para Azure OpenAI)

**Entrada**: Ninguna (genera datos desde cero)
**Salida**: `data/raw/intent_examples.json` con estructura:
```json
{
  "comprar": ["Me gustaría comprar esta camiseta", "..."],
  "devolver": ["Quiero devolver este producto", "..."],
  ...
}
```

### 🔸 **02_create_prompts.py** - Generar Prompts para Entrenamiento
**Propósito**: Convierte los ejemplos JSON en prompts estructurados para fine-tuning.

**Qué hace**:
- Lee el archivo `intent_examples.json` del paso anterior
- Crea un prompt del sistema que explica la tarea de clasificación
- Para cada ejemplo, genera un prompt con 3 mensajes:
  - `system`: Instrucciones de clasificación
  - `user`: El texto del cliente
  - `assistant`: La intención correcta
- Valida que todos los prompts tengan el formato correcto
- Guarda en formato JSONL (línea por prompt) en `data/processed/training_prompts.jsonl`

**Entrada**: `data/raw/intent_examples.json`
**Salida**: `data/processed/training_prompts.jsonl` (48 prompts)

### 🔸 **03_split_data.py** - Dividir Datos en Entrenamiento/Validación
**Propósito**: Separa los datos en conjuntos de entrenamiento y validación de forma balanceada.

**Qué hace**:
- Carga los 48 prompts del paso anterior
- Agrupa por intención para asegurar balance
- Divide cada intención: 80% entrenamiento (9 ejemplos) + 20% validación (3 ejemplos)
- Mezcla aleatoriamente cada conjunto (con seed=42 para reproducibilidad)
- Valida que todas las intenciones estén presentes en ambos conjuntos
- Guarda archivos separados para entrenamiento y validación

**Entrada**: `data/processed/training_prompts.jsonl`
**Salida**: 
- `data/training/train_data.jsonl` (36 prompts)
- `data/validation/validation_data.jsonl` (12 prompts)

### 🔸 **04_prepare_data.py** - Preparar Datos para Fine-Tuning
**Propósito**: Valida y prepara los datos finales asegurando cumplimiento con Azure OpenAI.

**Qué hace**:
- Carga datos de entrenamiento y validación
- Valida formato requerido por Azure OpenAI:
  - Estructura de mensajes correcta (system/user/assistant)
  - Contenido no vacío en cada mensaje
  - Termina con respuesta del assistant
- Calcula estadísticas: número de tokens estimados, ejemplos por conjunto
- Crea resumen con métricas y estado de validación
- Confirma que está listo para fine-tuning

**Entrada**: `train_data.jsonl` + `validation_data.jsonl`
**Salida**: `data/processed/data_preparation_summary.json` (métricas)

### 🔸 **05_fine_tuning.py** - Ejecutar Fine-Tuning en Azure
**Propósito**: Realiza el entrenamiento del modelo usando la API de Azure OpenAI.

**Qué hace**:
- Conecta con Azure OpenAI usando credenciales del `.env`
- Sube archivos de entrenamiento y validación a Azure
- Espera a que Azure procese los archivos (estado "processed")
- Inicia job de fine-tuning con hiperparámetros configurados:
  - Modelo base: `gpt-4o-mini` (o el definido en `.env`)
  - Epochs: 3, Batch size: 1, Learning rate: 0.1
- Monitorea progreso del fine-tuning en tiempo real
- Guarda información del modelo final y job ID

**Entrada**: Archivos de datos preparados
**Salida**: `results/fine_tuning_info.json` (ID del modelo entrenado)

### 🔸 **06_deploy_model.py** - Verificar Estado del Deployment
**Propósito**: Verifica el estado del deployment del modelo fine-tuned creado manualmente en Azure Portal.

**Qué hace**:
- Carga información del modelo fine-tuned del paso anterior
- Verifica que el job de fine-tuning esté completado exitosamente
- **🆕 Busca deployments existentes** en Azure OpenAI usando la API
- Reporta el estado actual del deployment:
  - ✅ **"succeeded"** → Listo para usar
  - ⏳ **"creating"** → En proceso de creación
  - ❌ **Otros estados** → Requiere atención
- Crea documentación de uso con la configuración correcta
- Guarda información del deployment para los siguientes pasos

**Nota**: ⚠️ Este script **NO crea** el deployment, solo **verifica su estado**. El deployment debe crearse manualmente en Azure Portal debido a limitaciones de la API.

**Entrada**: `results/fine_tuning_info.json`
**Salida**: `results/deployment_info.json` (información del deployment + guía de uso)

### 🔸 **07_test_model.py** - Probar Modelo con Casos de Prueba
**Propósito**: Evalúa el rendimiento del modelo con casos de prueba nuevos.

**Qué hace**:
- Carga el modelo fine-tuned desplegado
- Crea 15+ casos de prueba diversos:
  - Casos típicos para cada intención
  - Casos ambiguos para probar robustez
  - Frases con variaciones de longitud/estilo
- Ejecuta predicciones con el modelo
- Calcula métricas de rendimiento:
  - Accuracy general y por intención
  - Casos correctos vs incorrectos
  - Matriz de confusión implícita
- Identifica patrones de error

**Entrada**: Modelo desplegado
**Salida**: `results/test_results.json` (métricas detalladas)

### 🔸 **08_analyze_results.py** - Analizar Resultados y Mejoras
**Propósito**: Analiza el rendimiento y genera recomendaciones de mejora.

**Qué hace**:
- Carga resultados de pruebas y info de fine-tuning
- Analiza patrones de accuracy:
  - Mejor/peor intención performante
  - Varianza entre intenciones
  - Casos de fallo más comunes
- Genera sugerencias específicas:
  - Si accuracy <70%: más datos, revisar etiquetas
  - Si desbalanceado: más ejemplos para intenciones débiles
  - Ajustes de hiperparámetros recomendados
- Crea roadmap de próximos pasos
- Califica rendimiento (A+ a F) y da recomendaciones

**Entrada**: Todos los resultados anteriores
**Salida**: `results/improvement_analysis.json` (reporte completo)

## � Flujo de Datos Entre Scripts

```
01_create_examples.py
         ↓ (genera)
    intent_examples.json (48 ejemplos)
         ↓ (lee)
02_create_prompts.py
         ↓ (genera)
    training_prompts.jsonl (48 prompts)
         ↓ (lee)
03_split_data.py
         ↓ (divide)
    train_data.jsonl (36) + validation_data.jsonl (12)
         ↓ (valida)
04_prepare_data.py
         ↓ (confirma formato)
    data_preparation_summary.json
         ↓ (usa archivos)
05_fine_tuning.py
         ↓ (entrena modelo)
    fine_tuning_info.json (model ID)
         ↓ (verifica)
06_deploy_model.py
         ↓ (documenta uso)
    deployment_info.json
         ↓ (usa modelo)
07_test_model.py
         ↓ (evalúa)
    test_results.json (métricas)
         ↓ (analiza)
08_analyze_results.py
         ↓ (genera)
    improvement_analysis.json (recomendaciones)
```

## 📁 Archivos Generados por Carpeta

### `data/raw/`
- `intent_examples.json` - Ejemplos originales por intención

### `data/processed/`
- `training_prompts.jsonl` - Prompts formateados para fine-tuning
- `data_preparation_summary.json` - Estadísticas de preparación

### `data/training/`
- `train_data.jsonl` - Conjunto de entrenamiento (36 ejemplos)

### `data/validation/`
- `validation_data.jsonl` - Conjunto de validación (12 ejemplos)

### `results/`
- `fine_tuning_info.json` - Información del job y modelo entrenado
- `deployment_info.json` - Guía de uso del modelo desplegado
- `test_results.json` - Resultados de las pruebas de rendimiento
- `improvement_analysis.json` - Análisis y recomendaciones de mejora

## �🚀 Guía de Uso Rápido

### 1. Configuración inicial
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
# Editar .env con tus credenciales de Azure (ver sección "Configuración del Archivo .env")
# IMPORTANTE: Configurar FINE_TUNED_MODEL_DEPLOYMENT después del deployment manual
```

### 2. Ejecutar paso a paso
```bash
# Paso 1: Crear ejemplos
python scripts/01_create_examples.py

# Paso 2: Crear prompts  
python scripts/02_create_prompts.py

# ... continuar con cada paso
```

### 3. Ejecutar proceso completo
```bash
# Ejecutar todos los pasos automáticamente
python run_all_steps.py
```

## ⚙️ Configuración del Archivo .env

El archivo `.env` debe contener las siguientes variables de entorno para conectar con Azure OpenAI:

```bash
# Configuración de Azure OpenAI
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
AZURE_OPENAI_VERSION=2024-12-01-preview
AZURE_OPENAI_MODEL=gpt-4o-mini

# Deployment del modelo fine-tuned (configurar después del Paso 5)
FINE_TUNED_MODEL_DEPLOYMENT=gpt-4o-mini-2024-07-18-ft-d0f4b746b7f44e9f82d81f949f823655

# Parámetros opcionales de fine-tuning
FINE_TUNING_EPOCHS=3
FINE_TUNING_BATCH_SIZE=1
FINE_TUNING_LR_MULT=0.1
FINE_TUNING_PROMPT_LOSS_WEIGHT=0.01

# División de datos
TRAIN_SPLIT=0.8
VALIDATION_SPLIT=0.2
```

### 📝 **Notas importantes:**
- `AZURE_OPENAI_ENDPOINT`: URL de tu instancia de Azure OpenAI
- `AZURE_OPENAI_KEY`: Clave de API de Azure OpenAI (se encuentra en Azure Portal)
- `AZURE_OPENAI_VERSION`: Versión de API (usa `2024-12-01-preview` para fine-tuning)
- `FINE_TUNED_MODEL_DEPLOYMENT`: Nombre del deployment del modelo fine-tuned (se configura después del Paso 6 manual)

## 📋 Checklist por Paso

- [ ] **Paso 1**: Ejemplos JSON creados en `data/raw/`
- [ ] **Paso 2**: Prompts JSONL generados en `data/processed/`  
- [ ] **Paso 3**: Datos divididos en `data/training/` y `data/validation/`
- [ ] **Paso 4**: Formato validado para fine-tuning
- [ ] **Paso 5**: Modelo fine-tuned en Azure OpenAI
- [ ] **Paso 6**: ⚠️ **Deployment manual en Azure Portal** + verificación con script
- [ ] **Paso 7**: Modelo testeado con casos de prueba
- [ ] **Paso 8**: Análisis de resultados completado
- [ ] **Paso 6**: Modelo desplegado y accesible
- [ ] **Paso 7**: Pruebas ejecutadas con métricas
- [ ] **Paso 8**: Análisis y recomendaciones generadas