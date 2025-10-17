# Prompts para el sistema y el usuario en el ejercicio de extracción de fechas
import os

# System Message
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

# Cargar mensajes de usuario desde archivos en la carpeta text_examples
text_examples_dir = os.path.join(os.path.dirname(__file__), "..", "text_examples")
user_messages = []

for filename in sorted(os.listdir(text_examples_dir)):
    if filename.endswith(".txt"):
        with open(os.path.join(text_examples_dir, filename), "r", encoding="utf-8") as file:
            user_messages.append(file.read().strip())