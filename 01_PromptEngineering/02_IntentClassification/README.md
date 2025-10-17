# 🧩 Ejercicio 2:  Clasificación de Intenciones (Intent Classification)

---

## 🔹 Descripción

En este ejercicio, simularemos ser un bot de un banco. El objetivo es **detectar la intención del usuario** a partir de frases y clasificarlas en una de las siguientes categorías:

### 🏦 Categorías de Intenciones

1. **Consulta de saldo**  
   Permite al usuario revisar el saldo de sus cuentas bancarias, incluyendo:
   - Saldo disponible y contable.
   - Saldo pendiente de cargos futuros o autorizaciones.
   - Detalles de intereses acumulados o cargos aplicados.
   - Fechas de corte y próximos estados de cuenta.
   - Opción de ver historial de transacciones.

2. **Gestión de tarjetas**  
   Servicios relacionados con tarjetas de débito y crédito:
   - Bloqueo/desbloqueo temporal por pérdida, robo o fraude.
   - Solicitud de reemplazo de tarjeta dañada o vencida.
   - Cambio de PIN o contraseña.
   - Personalización de límites de gasto diarios o mensuales.
   - Activación de servicios asociados (seguros de viaje, programas de recompensas, etc.).

3. **Apertura de cuentas o contratación de productos**  
   Iniciar procesos de apertura de cuentas o contratar productos financieros:
   - Información y requisitos para abrir cuentas.
   - Contratar depósitos a plazo, fondos de inversión o planes de ahorro.
   - Solicitar préstamos personales, hipotecarios o líneas de crédito.
   - Calculadoras de préstamos o simuladores de ahorro/inversión.
   - Envío de documentación inicial o agendar citas para finalizar el trámite.

4. **Ayuda y soporte técnico**  
   Asistencia con problemas o dudas sobre la app bancaria:
   - Recuperar o cambiar contraseñas y accesos.
   - Problemas de acceso u operación de la app.
   - Actualización de datos personales o de contacto.
   - Información sobre cómo realizar transacciones o usar nuevas funciones.
   - Soporte ante errores de la aplicación o servicios online.

5. **Otro**  
   Si la frase no pertenece a ninguna de las categorías anteriores.

---

## 🗂️ Estructura de Carpetas

```plaintext
02_IntentClassification/
├── data/
│   ├── examples.txt          # Frases de ejemplo para clasificación
│   └── results/              # Carpeta para resultados generados
├── prompts/
│   ├── system_message.py     # Mensaje del sistema
│   ├── user_message.py       # Mensaje del usuario
│   └── prompt_builder.py     # Constructor de prompts
├── models/
│   └── modelo_4.py           # Script principal para GPT-4
├── .env                      # Variables de entorno
├── README.md                 # Documentación del proyecto
```

---

## ⚙️ Cómo Funciona el Ejercicio

### Flujo del Ejercicio

1. **Entrada**: El archivo `data/examples.txt` contiene frases de ejemplo que representan consultas de usuarios.
2. **Construcción del Prompt**:
   - `prompts/system_message.py` define el rol del modelo.
   - `prompts/user_message.py` genera el mensaje del usuario.
   - `prompts/prompt_builder.py` combina ambos mensajes en un prompt completo.

3. **Ejecución del Modelo**:
   - `models/modelo_4.py` utiliza el cliente de Azure OpenAI para enviar el prompt al modelo GPT-4.
   - El modelo devuelve la intención clasificada.

4. **Salida**: Los resultados se guardan en `data/results/gpt-4-results.json`.

### Comandos para Ejecutar


1. **Ejecutar el Script**:

   ```powershell
   cd "C:\Users\marta.fraile.jara\Documents\TrainingExercises\openAI\01_ PromptEngineering\02_IntentClassification"
   C:/Users/marta.fraile.jara/AppData/Local/anaconda3/python.exe -m models.modelo_4
   ```

---

## 🎯 Objetivo del Ejercicio

Clasificar correctamente cada frase en una de las categorías usando **GPT-4**, siguiendo estas indicaciones:

1. Seguir la checklist de prompt engineering.
2. Especificar `system_message` y `user_message`.
3. Probar todas las frases.

---

## 💡 Pistas

- Si la frase no pertenece a ninguna categoría, clasifícala como **Otro**.
- Solo hay que detectar la intención del usuario, **no realizar la acción**.
