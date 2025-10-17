"""
Paso 1: Crear archivo JSON con ejemplos de intenciones
"""

import json
import os
import sys
from typing import Dict, List

# Agregar el directorio padre al path para imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from config.config import Config

def create_intent_examples() -> Dict[str, List[str]]:
    """
    Crea ejemplos de intenciones para la tienda
    Retorna un diccionario con 4 intenciones y 12 ejemplos cada una (48 total)
    Mínimo requerido por Azure OpenAI: 10 ejemplos
    """
    
    examples = {
        "comprar": [
            "Me gustaría comprar esta camiseta",
            "Estaba buscando unos pantalones pitillos", 
            "¿Podría enseñarme prendas con estampados florales?",
            "Quiero llevarme este vestido azul",
            "¿Cuánto cuesta esta chaqueta de cuero?",
            "Me interesa comprar esos zapatos negros",
            "Quisiera adquirir esta bufanda",
            "¿Tienen esta blusa en talla M?",
            "Me encanta este abrigo, lo quiero",
            "Voy a comprar estos vaqueros",
            "¿Puedo pagar con tarjeta esta falda?",
            "Necesito una corbata para una boda"
        ],
        "devolver": [
            "Quiero devolver este producto",
            "Esta prenda no me queda bien, ¿puedo cambiarla?",
            "Necesito hacer una devolución de esta compra",
            "Este pantalón me queda grande, ¿puedo cambiarlo?",
            "La camiseta tiene un defecto, quiero devolverla",
            "¿Cuál es su política de devoluciones?",
            "No me gusta como me queda, ¿puedo devolverlo?",
            "Este producto no es lo que esperaba",
            "¿Puedo cambiar esta talla por una más pequeña?",
            "El color no es el que pedí, quiero cambiarlo",
            "¿Hasta cuándo puedo devolver esta compra?",
            "Necesito el reembolso de esta prenda"
        ],
        "queja": [
            "Tengo una queja sobre el servicio recibido",
            "La atención al cliente ha sido muy mala",
            "Quiero presentar una reclamación formal",
            "El vendedor fue muy grosero conmigo",
            "Esta tienda tiene un servicio pésimo",
            "Me trataron muy mal en el probador",
            "La empleada fue muy descortés",
            "Quiero hablar con el gerente por el mal servicio",
            "El personal no me ayudó nada",
            "Estoy muy insatisfecho con la atención",
            "Voy a poner una queja en el libro de reclamaciones",
            "Su servicio post-venta es terrible"
        ],
        "consulta": [
            "¿Qué tallas tienen disponibles?",
            "¿Cuál es el horario de la tienda?",
            "¿Aceptan tarjetas de crédito?",
            "¿Dónde está el probador?",
            "¿Tienen descuentos en esta época?",
            "¿Cuándo llega la nueva colección?",
            "¿Hacen envíos a domicilio?",
            "¿Tienen tallas grandes disponibles?",
            "¿A qué hora cierran hoy?",
            "¿Dónde puedo aparcar cerca de aquí?",
            "¿Tienen programa de fidelización?",
            "¿Cuáles son sus métodos de pago?"
        ]
    }
    
    return examples

def save_examples_to_json(examples: Dict[str, List[str]], filepath: str) -> None:
    """Guarda los ejemplos en un archivo JSON"""
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(examples, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Ejemplos guardados en: {filepath}")

def main():
    """Función principal para ejecutar el Paso 1"""
    
    print("=== PASO 1: Crear archivo JSON con ejemplos ===")
    
    # Crear ejemplos
    examples = create_intent_examples()
    
    # Mostrar ejemplos creados
    print("\n📝 Ejemplos creados:")
    for intent, phrases in examples.items():
        print(f"\n{intent.upper()}:")
        for i, phrase in enumerate(phrases, 1):
            print(f"  {i}. {phrase}")
    
    # Guardar en archivo JSON
    filepath = os.path.join(Config.RAW_DATA_PATH, "intent_examples.json")
    save_examples_to_json(examples, filepath)
    
    # Validar que se creó correctamente
    if os.path.exists(filepath):
        print(f"\n✅ Paso 1 completado exitosamente")
        print(f"📁 Archivo creado: {filepath}")
    else:
        print(f"\n❌ Error: No se pudo crear el archivo")

if __name__ == "__main__":
    main()