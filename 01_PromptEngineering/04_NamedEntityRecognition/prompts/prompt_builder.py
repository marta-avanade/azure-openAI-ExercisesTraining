# Script para construir prompts dinámicos

def build_prompt(system_message, user_message, input_text):
    return f"{system_message}\n\n{user_message}\n\nTexto: {input_text}"