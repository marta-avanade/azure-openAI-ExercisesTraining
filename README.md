# 🚀 Azure OpenAI Training Exercises

Este repositorio contiene una colección completa de ejercicios prácticos para aprender y dominar Azure OpenAI, desde conceptos básicos hasta técnicas avanzadas.

## 📚 Contenido del Repositorio

### 🎯 **01_PromptEngineering**
Ejercicios fundamentales de ingeniería de prompts:
- **01_DatesExtractor**: Extracción de fechas de texto usando diferentes modelos
- **02_IntentClassification**: Clasificación de intenciones de usuarios
- **03_CategorizationClaims**: Categorización de reclamaciones
- **04_NamedEntityRecognition**: Reconocimiento de entidades nombradas

### 🔍 **02_Embedding**
Trabajo con embeddings y búsqueda semántica:
- Procesamiento de documentos PDF
- Creación de embeddings vectoriales
- Implementación de RAG (Retrieval-Augmented Generation)
- Sistema de preguntas y respuestas

### 🎛️ **03_FineTunning**
Fine-tuning completo de modelos:
- **Pipeline de 8 pasos** desde datos hasta deployment
- Generación automática de datasets
- Entrenamiento en Azure OpenAI
- Testing y análisis de resultados

## 🏗️ Estructura del Proyecto

```
azure-openAI-ExercisesTraining/
├── 01_PromptEngineering/          # Ejercicios básicos y avanzados de prompts
├── 02_Embedding/                  # RAG y embeddings vectoriales
├── 03_FineTunning/               # Fine-tuning completo end-to-end
├── .gitignore                    # Exclusiones de git
└── README.md                     # Este archivo
```

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.8+
- Cuenta de Azure con acceso a OpenAI
- Visual Studio Code (recomendado)

### Configuración Inicial
1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/marta-avanade/azure-openAI-ExercisesTraining.git
   cd azure-openAI-ExercisesTraining
   ```

2. **Configurar variables de entorno**:
   - Crear archivo `.env` en cada proyecto con tus credenciales de Azure
   - Ejemplo para 03_FineTunning:
   ```bash
   AZURE_OPENAI_ENDPOINT=https://tu-endpoint.openai.azure.com/
   AZURE_OPENAI_KEY=tu-api-key
   AZURE_OPENAI_VERSION=2024-12-01-preview
   ```

3. **Instalar dependencias**:
   ```bash
   # Para cada proyecto, navegar a su carpeta e instalar
   cd 03_FineTunning
   pip install -r requirements.txt
   ```

## 🎯 Ejercicios Recomendados por Nivel

### 🟢 **Principiante**
1. **01_PromptEngineering/01_DatesExtractor** - Conceptos básicos
2. **01_PromptEngineering/02_IntentClassification** - Clasificación simple
3. **02_Embedding** - Búsqueda semántica básica

### 🟡 **Intermedio**
1. **01_PromptEngineering/03_CategorizationClaims** - Prompts avanzados
2. **01_PromptEngineering/04_NamedEntityRecognition** - NER personalizado
3. **02_Embedding** (RAG completo) - Sistema Q&A avanzado

### 🔴 **Avanzado**
1. **03_FineTunning** - Pipeline completo de fine-tuning
2. Combinación de múltiples técnicas
3. Optimización de rendimiento y costos

## 📖 Documentación Detallada

Cada ejercicio incluye:
- **README.md** específico con instrucciones paso a paso
- **Scripts numerados** para ejecución secuencial
- **Ejemplos de datos** y casos de prueba
- **Análisis de resultados** y métricas

### Documentos Principales:
- `01_PromptEngineering/README.md` - Guía de ingeniería de prompts
- `02_Embedding/README.md` - Embeddings y RAG
- `03_FineTunning/README.md` - Fine-tuning completo
- `03_FineTunning/ESTRUCTURA.md` - Estructura detallada del proyecto

## 🛡️ Seguridad y Buenas Prácticas

- ✅ **Archivos .env excluidos** del repositorio
- ✅ **Datos sensibles no incluidos** en git
- ✅ **Estructura de carpetas mantenida** con .gitkeep
- ✅ **Configuración por entorno** separada

## 🤝 Contribuciones

Este repositorio está diseñado para fines educativos. Para sugerencias o mejoras:

1. Fork del repositorio
2. Crear branch para tu feature
3. Commit de cambios
4. Push al branch
5. Crear Pull Request

## 📄 Licencia

Proyecto educativo para formación en Azure OpenAI.

## 📞 Contacto

- **Autor**: Marta Fraile Jara
- **Organización**: Avanade
- **Repositorio**: [azure-openAI-ExercisesTraining](https://github.com/marta-avanade/azure-openAI-ExercisesTraining)

---
🎓 **¡Comienza tu journey en Azure OpenAI explorando los ejercicios paso a paso!**