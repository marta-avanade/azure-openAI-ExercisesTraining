"""
Paso 4: Preparar los datos para fine-tuning
"""

import json
import os
import sys
from typing import List, Dict

# Agregar el directorio padre al path para imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from config.config import Config

def validate_training_format(data: List[Dict]) -> bool:
    """
    Valida que los datos estén en el formato correcto para fine-tuning de OpenAI
    """
    
    print("🔍 Validando formato de datos para fine-tuning...")
    
    for i, item in enumerate(data):
        # Verificar estructura básica
        if "messages" not in item:
            print(f"❌ Item {i+1}: Falta campo 'messages'")
            return False
        
        messages = item["messages"]
        
        # Verificar número de mensajes
        if len(messages) < 2:
            print(f"❌ Item {i+1}: Debe tener al menos 2 mensajes (user y assistant)")
            return False
        
        # Verificar roles
        valid_roles = {"system", "user", "assistant"}
        for j, msg in enumerate(messages):
            if "role" not in msg or msg["role"] not in valid_roles:
                print(f"❌ Item {i+1}, Mensaje {j+1}: Rol inválido")
                return False
            
            if "content" not in msg or not msg["content"].strip():
                print(f"❌ Item {i+1}, Mensaje {j+1}: Contenido vacío")
                return False
        
        # Verificar que termine con assistant
        if messages[-1]["role"] != "assistant":
            print(f"❌ Item {i+1}: Debe terminar con un mensaje del assistant")
            return False
    
    print(f"✅ Formato válido para {len(data)} ejemplos")
    return True

def calculate_tokens_estimate(data: List[Dict]) -> Dict[str, int]:
    """
    Estima el número de tokens en los datos (aproximación simple)
    """
    
    total_chars = 0
    total_examples = len(data)
    
    for item in data:
        for message in item["messages"]:
            total_chars += len(message["content"])
    
    # Aproximación: 1 token ≈ 4 caracteres en español
    estimated_tokens = total_chars // 4
    
    return {
        "total_examples": total_examples,
        "total_characters": total_chars,
        "estimated_tokens": estimated_tokens,
        "tokens_per_example": estimated_tokens // total_examples if total_examples > 0 else 0
    }

def create_training_summary(train_stats: Dict, val_stats: Dict) -> Dict:
    """Crea un resumen de los datos preparados"""
    
    summary = {
        "training_data": train_stats,
        "validation_data": val_stats,
        "total_examples": train_stats["total_examples"] + val_stats["total_examples"],
        "total_estimated_tokens": train_stats["estimated_tokens"] + val_stats["estimated_tokens"],
        "format_validation": "PASSED",
        "ready_for_finetuning": True
    }
    
    return summary

def save_prepared_data_info(summary: Dict) -> None:
    """Guarda información sobre los datos preparados"""
    
    info_path = os.path.join(Config.PROCESSED_DATA_PATH, "data_preparation_summary.json")
    
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"📊 Resumen guardado en: {info_path}")

def main():
    """Función principal para ejecutar el Paso 4"""
    
    print("=== PASO 4: Preparar los datos ===")
    
    # Rutas de datos
    train_path = os.path.join(Config.TRAINING_DATA_PATH, "train_data.jsonl")
    val_path = os.path.join(Config.VALIDATION_DATA_PATH, "validation_data.jsonl")
    
    # Verificar que existan los archivos
    if not os.path.exists(train_path):
        print(f"❌ Error: No se encontró {train_path}")
        print("   Ejecuta primero el Paso 3")
        return
    
    if not os.path.exists(val_path):
        print(f"❌ Error: No se encontró {val_path}")
        print("   Ejecuta primero el Paso 3")
        return
    
    # Cargar datos
    print("📂 Cargando datos...")
    
    train_data = []
    with open(train_path, 'r', encoding='utf-8') as f:
        for line in f:
            train_data.append(json.loads(line.strip()))
    
    val_data = []
    with open(val_path, 'r', encoding='utf-8') as f:
        for line in f:
            val_data.append(json.loads(line.strip()))
    
    print(f"📊 Datos cargados:")
    print(f"   - Entrenamiento: {len(train_data)} ejemplos")
    print(f"   - Validación: {len(val_data)} ejemplos")
    
    # Validar formato
    print(f"\n🔍 Validando formato de entrenamiento...")
    if not validate_training_format(train_data):
        print("❌ Error en formato de datos de entrenamiento")
        return
    
    print(f"\n🔍 Validando formato de validación...")
    if not validate_training_format(val_data):
        print("❌ Error en formato de datos de validación")
        return
    
    # Calcular estadísticas
    print(f"\n📊 Calculando estadísticas...")
    train_stats = calculate_tokens_estimate(train_data)
    val_stats = calculate_tokens_estimate(val_data)
    
    print(f"\n📈 Estadísticas de entrenamiento:")
    print(f"   - Ejemplos: {train_stats['total_examples']}")
    print(f"   - Tokens estimados: {train_stats['estimated_tokens']:,}")
    print(f"   - Tokens por ejemplo: {train_stats['tokens_per_example']}")
    
    print(f"\n📈 Estadísticas de validación:")
    print(f"   - Ejemplos: {val_stats['total_examples']}")
    print(f"   - Tokens estimados: {val_stats['estimated_tokens']:,}")
    print(f"   - Tokens por ejemplo: {val_stats['tokens_per_example']}")
    
    # Crear resumen
    summary = create_training_summary(train_stats, val_stats)
    save_prepared_data_info(summary)
    
    # Mostrar resumen final
    print(f"\n✅ Paso 4 completado exitosamente")
    print(f"🚀 Los datos están listos para fine-tuning:")
    print(f"   - Total de ejemplos: {summary['total_examples']}")
    print(f"   - Total de tokens estimados: {summary['total_estimated_tokens']:,}")
    print(f"   - Validación de formato: {summary['format_validation']}")
    
    print(f"\n📁 Archivos preparados:")
    print(f"   - Entrenamiento: {train_path}")
    print(f"   - Validación: {val_path}")

if __name__ == "__main__":
    main()