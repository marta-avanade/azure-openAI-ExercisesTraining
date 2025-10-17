# 03 - Fine-Tuning

## Descripción del Ejercicio

Este ejercicio se enfoca en el **Fine-Tuning para Clasificación de Textos en Acciones de Tienda**. El objetivo es entrenar un modelo para clasificar textos según las acciones que se pueden realizar en una tienda, como comprar, devolver un producto, presentar una queja, etc.

## Pasos del Ejercicio

### ✅ Paso 1: Crear archivo JSON con ejemplos

- Crear un archivo JSON propio siguiendo el mismo formato del ejemplo
- Incluir **4 intenciones (intents)** diferentes
- Cada intención debe tener **3 frases de ejemplo** que correspondan a esa intención

#### Ejemplo de formato JSON:

```json
{
    "comprar": [
        "Me gustaría comprar esta camiseta",
        "Estaba buscando unos pantalones pitillos",
        "¿Podría enseñarme prendas con estampados florales?"
    ]
}
```

> **Nota:** Todas las frases del ejemplo pertenecen a la intención "comprar".

### ✅ Paso 2: Crear y verificar prompts

- Generar los prompts a partir del JSON creado
- Comprobar que los prompts se han creado correctamente

### ✅ Paso 3: Dividir los datos

- Separar los datos en conjuntos de entrenamiento y validación siguiendo buenas prácticas

### ✅ Paso 4: Preparar los datos

- Asegurarse de que los datos estén en el formato adecuado para el fine-tuning

### ✅ Paso 5: Realizar Fine-Tuning

- Ajustar el modelo con los datos preparados para que aprenda a clasificar correctamente las intenciones

### ✅ Paso 6: Desplegar el modelo

- Poner el modelo en un entorno de prueba o producción para evaluar su funcionamiento

### ✅ Paso 7: Probar el modelo

- Realizar pruebas con ejemplos nuevos para verificar la precisión y efectividad del modelo

✅ Paso 8: Analizar resultados y mejorar

- Obtener conclusiones sobre el rendimiento del modelo.
- Considerar posibles mejoras para optimizar el acelerador.