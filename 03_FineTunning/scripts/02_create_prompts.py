"""
Paso 2: Crear y verificar prompts
"""

import json
import os
import sys
from typing import Dict, List, Tuple

# Agregar el directorio padre al path para imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from config.config import Config

def create_system_prompt() -> str:
    """Crea el prompt del sistema para clasificación de intenciones"""
    
    system_prompt = """Eres un asistente especializado en clasificar las intenciones de los clientes en una tienda de ropa.

Tu tarea es clasificar cada mensaje del usuario en una de las siguientes categorías:
- comprar: El usuario quiere adquirir un producto
- devolver: El usuario quiere devolver o cambiar un producto
- queja: El usuario tiene una queja o reclamación
- consulta: El usuario hace preguntas informativas

Responde únicamente con el nombre de la categoría (comprar, devolver, queja, consulta)."""

    return system_prompt

def create_training_prompts(examples: Dict[str, List[str]]) -> List[Dict]:
    """
    Convierte los ejemplos en formato de prompts para fine-tuning
    """
    
    system_prompt = create_system_prompt()
    prompts = []
    
    for intent, phrases in examples.items():
        for phrase in phrases:
            prompt_data = {
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": phrase
                    },
                    {
                        "role": "assistant",
                        "content": intent
                    }
                ]
            }
            prompts.append(prompt_data)
    
    return prompts

def verify_prompts(prompts: List[Dict]) -> bool:
    """Verifica que los prompts tengan el formato correcto"""
    
    print("🔍 Verificando prompts...")
    
    required_roles = {"system", "user", "assistant"}
    
    for i, prompt in enumerate(prompts):
        # Verificar estructura
        if "messages" not in prompt:
            print(f"❌ Prompt {i+1}: Falta campo 'messages'")
            return False
            
        messages = prompt["messages"]
        if len(messages) != 3:
            print(f"❌ Prompt {i+1}: Debe tener exactamente 3 mensajes")
            return False
        
        # Verificar roles
        roles = {msg["role"] for msg in messages}
        if roles != required_roles:
            print(f"❌ Prompt {i+1}: Roles incorrectos. Se encontró: {roles}")
            return False
            
        # Verificar contenido
        for msg in messages:
            if not msg.get("content"):
                print(f"❌ Prompt {i+1}: Mensaje vacío para rol '{msg['role']}'")
                return False
    
    print(f"✅ Todos los {len(prompts)} prompts son válidos")
    return True

def save_prompts(prompts: List[Dict], filepath: str) -> None:
    """Guarda los prompts en formato JSONL"""
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for prompt in prompts:
            f.write(json.dumps(prompt, ensure_ascii=False) + '\n')
    
    print(f"✅ Prompts guardados en: {filepath}")

def main():
    """Función principal para ejecutar el Paso 2"""
    
    print("=== PASO 2: Crear y verificar prompts ===")
    
    # Cargar ejemplos del paso anterior
    examples_path = os.path.join(Config.RAW_DATA_PATH, "intent_examples.json")
    
    if not os.path.exists(examples_path):
        print(f"❌ Error: No se encontró el archivo de ejemplos en {examples_path}")
        print("   Ejecuta primero el Paso 1")
        return
    
    with open(examples_path, 'r', encoding='utf-8') as f:
        examples = json.load(f)
    
    print(f"📂 Ejemplos cargados desde: {examples_path}")
    
    # Crear prompts
    prompts = create_training_prompts(examples)
    print(f"📝 Se crearon {len(prompts)} prompts")
    
    # Mostrar un ejemplo de prompt
    print("\n🔍 Ejemplo de prompt generado:")
    print(json.dumps(prompts[0], ensure_ascii=False, indent=2))
    
    # Verificar prompts
    if verify_prompts(prompts):
        # Guardar prompts
        prompts_path = os.path.join(Config.PROCESSED_DATA_PATH, "training_prompts.jsonl")
        save_prompts(prompts, prompts_path)
        
        print(f"\n✅ Paso 2 completado exitosamente")
        print(f"📁 Prompts guardados en: {prompts_path}")
    else:
        print(f"\n❌ Error en la verificación de prompts")

if __name__ == "__main__":
    main()