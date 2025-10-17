# Mensaje del usuario con instrucciones

def get_user_message():
    """
    Devuelve el mensaje del usuario para el modelo.

    Returns:
        str: Mensaje del usuario.
    """
    return (
        "Tarea: Dado el siguiente texto, extrae TODAS las entidades y clasifícalas en uno de estos tipos: "
        "Concepto, Localización, Tiempo. "
        "Salida obligatoria: Devuelve SOLO una lista JSON (array) de objetos con claves exactas 'keyword' y 'type'. "
        "No añadas ningún otro texto. "
        "Normaliza: usa 'Localización' como tipo (no sinónimos). "
        "Ejemplo de salida: [{\"keyword\": \"Dirección Territorial\", \"type\": \"Localización\"}]."
    )