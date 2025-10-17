# Construye el prompt combinando el mensaje del sistema y del usuario
from prompts.system_message import get_system_message
from prompts.user_message import get_user_message

def build_prompt(user_input):
    system_message = get_system_message()
    user_message = get_user_message(user_input)
    return f"{system_message}\n{user_message}"