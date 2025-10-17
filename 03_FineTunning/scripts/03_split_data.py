"""
Paso 3: Dividir los datos en conjuntos de entrenamiento y validación
"""

import json
import os
import random
import sys
from typing import List, Dict, Tuple

# Agregar el directorio padre al path para imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from config.config import Config

def load_prompts(filepath: str) -> List[Dict]:
    """Carga los prompts desde archivo JSONL"""
    
    prompts = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            prompts.append(json.loads(line.strip()))
    
    return prompts

def split_data(prompts: List[Dict], train_ratio: float = 0.8) -> Tuple[List[Dict], List[Dict]]:
    """
    Divide los datos en conjuntos de entrenamiento y validación
    Asegura que cada intención tenga representación en ambos conjuntos
    """
    
    # Agrupar prompts por intención
    prompts_by_intent = {}
    for prompt in prompts:
        intent = prompt["messages"][2]["content"]  # respuesta del assistant
        if intent not in prompts_by_intent:
            prompts_by_intent[intent] = []
        prompts_by_intent[intent].append(prompt)
    
    train_data = []
    validation_data = []
    
    # Dividir cada intención por separado
    for intent, intent_prompts in prompts_by_intent.items():
        # Mezclar aleatoriamente
        shuffled = intent_prompts.copy()
        random.shuffle(shuffled)
        
        # Calcular división
        n_train = max(1, int(len(shuffled) * train_ratio))  # Mínimo 1 para entrenamiento
        
        train_data.extend(shuffled[:n_train])
        validation_data.extend(shuffled[n_train:])
        
        print(f"📊 {intent}: {n_train} entrenamiento, {len(shuffled) - n_train} validación")
    
    # Mezclar los conjuntos finales
    random.shuffle(train_data)
    random.shuffle(validation_data)
    
    return train_data, validation_data

def save_split_data(train_data: List[Dict], validation_data: List[Dict]) -> None:
    """Guarda los conjuntos de datos divididos"""
    
    # Guardar datos de entrenamiento
    train_path = os.path.join(Config.TRAINING_DATA_PATH, "train_data.jsonl")
    os.makedirs(os.path.dirname(train_path), exist_ok=True)
    
    with open(train_path, 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    # Guardar datos de validación
    val_path = os.path.join(Config.VALIDATION_DATA_PATH, "validation_data.jsonl")
    os.makedirs(os.path.dirname(val_path), exist_ok=True)
    
    with open(val_path, 'w', encoding='utf-8') as f:
        for item in validation_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"✅ Datos de entrenamiento guardados en: {train_path}")
    print(f"✅ Datos de validación guardados en: {val_path}")

def validate_split(train_data: List[Dict], validation_data: List[Dict]) -> bool:
    """Valida que la división sea correcta"""
    
    # Verificar que ambos conjuntos tengan datos
    if len(train_data) == 0:
        print("❌ Error: Conjunto de entrenamiento vacío")
        return False
    
    if len(validation_data) == 0:
        print("❌ Error: Conjunto de validación vacío")
        return False
    
    # Verificar que todas las intenciones estén representadas en entrenamiento
    train_intents = set()
    for item in train_data:
        intent = item["messages"][2]["content"]
        train_intents.add(intent)
    
    val_intents = set()
    for item in validation_data:
        intent = item["messages"][2]["content"]
        val_intents.add(intent)
    
    expected_intents = set(Config.INTENT_CATEGORIES)
    
    if train_intents != expected_intents:
        print(f"❌ Error: Intenciones faltantes en entrenamiento: {expected_intents - train_intents}")
        return False
    
    print(f"✅ Validación exitosa:")
    print(f"   - Entrenamiento: {len(train_data)} ejemplos con intenciones: {sorted(train_intents)}")
    print(f"   - Validación: {len(validation_data)} ejemplos con intenciones: {sorted(val_intents)}")
    
    return True

def main():
    """Función principal para ejecutar el Paso 3"""
    
    print("=== PASO 3: Dividir los datos ===")
    
    # Cargar prompts del paso anterior
    prompts_path = os.path.join(Config.PROCESSED_DATA_PATH, "training_prompts.jsonl")
    
    if not os.path.exists(prompts_path):
        print(f"❌ Error: No se encontró el archivo de prompts en {prompts_path}")
        print("   Ejecuta primero el Paso 2")
        return
    
    prompts = load_prompts(prompts_path)
    print(f"📂 Cargados {len(prompts)} prompts desde: {prompts_path}")
    
    # Configurar semilla para reproducibilidad
    random.seed(42)
    
    # Dividir datos
    print(f"\n📊 Dividiendo datos (entrenamiento: {Config.TRAIN_SPLIT:.0%}, validación: {Config.VALIDATION_SPLIT:.0%})")
    train_data, validation_data = split_data(prompts, Config.TRAIN_SPLIT)
    
    # Validar división
    if validate_split(train_data, validation_data):
        # Guardar datos divididos
        save_split_data(train_data, validation_data)
        
        print(f"\n✅ Paso 3 completado exitosamente")
        print(f"📈 Total: {len(prompts)} ejemplos divididos en:")
        print(f"   - Entrenamiento: {len(train_data)} ejemplos")
        print(f"   - Validación: {len(validation_data)} ejemplos")
    else:
        print(f"\n❌ Error en la validación de la división")

if __name__ == "__main__":
    main()