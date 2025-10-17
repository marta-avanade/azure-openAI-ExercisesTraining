"""
Paso 7: Probar el modelo fine-tuned
"""

import json
import os
import sys
from typing import List, Dict, Tuple
from openai import AzureOpenAI

# Agregar el directorio padre al path para imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from config.config import Config

class ModelTester:
    """Gestiona las pruebas del modelo fine-tuned"""
    
    def __init__(self):
        """Inicializa el cliente y carga el modelo"""
        
        if not Config.validate_config():
            raise ValueError("Configuración de Azure OpenAI incompleta")
        
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_KEY,
            api_version=Config.AZURE_OPENAI_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        
        self.fine_tuned_model = None
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Crea el prompt del sistema para las pruebas"""
        
        return """Eres un asistente especializado en clasificar las intenciones de los clientes en una tienda de ropa.

Tu tarea es clasificar cada mensaje del usuario en una de las siguientes categorías:
- comprar: El usuario quiere adquirir un producto
- devolver: El usuario quiere devolver o cambiar un producto
- queja: El usuario tiene una queja o reclamación
- consulta: El usuario hace preguntas informativas

Responde únicamente con el nombre de la categoría (comprar, devolver, queja, consulta)."""
    
    def load_model_info(self) -> bool:
        """Carga información del modelo desplegado"""
        
        # Primero intentar usar el deployment configurado en .env
        if Config.FINE_TUNED_MODEL_DEPLOYMENT:
            self.fine_tuned_model = Config.FINE_TUNED_MODEL_DEPLOYMENT
            print(f"📂 Modelo fine-tuned (desde .env): {self.fine_tuned_model}")
            print(f"🔄 Fallback disponible: {Config.BASE_MODEL}")
            return True
        
        # Si no está en .env, intentar cargar desde deployment_info.json
        deploy_path = os.path.join(Config.RESULTS_PATH, "deployment_info.json")
        
        if os.path.exists(deploy_path):
            with open(deploy_path, 'r', encoding='utf-8') as f:
                info = json.load(f)
            
            self.fine_tuned_model = info.get("model_id")
            
            if self.fine_tuned_model:
                print(f"📂 Modelo fine-tuned (desde archivo): {self.fine_tuned_model}")
                print(f"🔄 Fallback disponible: {Config.BASE_MODEL}")
                return True
        
        # Si no se encuentra ninguna configuración
        print(f"⚠️ No se encontró configuración del modelo fine-tuned")
        print(f"   Usando modelo base: {Config.BASE_MODEL}")
        self.fine_tuned_model = Config.BASE_MODEL
        return True
    
    def create_test_cases(self) -> List[Dict[str, str]]:
        """Crea casos de prueba para evaluar el modelo"""
        
        test_cases = [
            # Casos de compra
            {"text": "Me interesa comprar esos zapatos negros", "expected": "comprar"},
            {"text": "¿Cuánto cuesta esta chaqueta?", "expected": "comprar"},
            {"text": "Quisiera llevarme este vestido", "expected": "comprar"},
            
            # Casos de devolución
            {"text": "Esta camisa me queda grande, ¿puedo cambiarla?", "expected": "devolver"},
            {"text": "Necesito devolver este pantalón", "expected": "devolver"},
            {"text": "¿Cuál es su política de devoluciones?", "expected": "devolver"},
            
            # Casos de queja
            {"text": "El vendedor fue muy grosero conmigo", "expected": "queja"},
            {"text": "Tengo una queja sobre el servicio al cliente", "expected": "queja"},
            {"text": "Esta tienda tiene un servicio pésimo", "expected": "queja"},
            
            # Casos de consulta
            {"text": "¿A qué hora cierran hoy?", "expected": "consulta"},
            {"text": "¿Tienen tallas grandes disponibles?", "expected": "consulta"},
            {"text": "¿Dónde está el probador?", "expected": "consulta"},
            
            # Casos ambiguos para probar robustez
            {"text": "No me gusta cómo me queda esta prenda", "expected": "devolver"},
            {"text": "¿Tienen descuentos en esta época?", "expected": "consulta"},
            {"text": "Me encanta esta tienda, quiero comprar todo", "expected": "comprar"}
        ]
        
        return test_cases
    
    def test_single_case(self, text: str) -> Tuple[str, bool]:
        """Prueba un caso individual con fallback al modelo base"""
        
        # Intentar primero con modelo fine-tuned
        try:
            response = self.client.chat.completions.create(
                model=self.fine_tuned_model,  # Usando el deployment del modelo fine-tuned
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            prediction = response.choices[0].message.content.strip().lower()
            return prediction, True
            
        except Exception as e:
            error_msg = str(e)
            
            # Si es error de deployment, usar modelo base como fallback
            if "DeploymentNotFound" in error_msg:
                try:
                    print(f"🔄 Usando modelo base como fallback...")
                    response = self.client.chat.completions.create(
                        model=Config.BASE_MODEL,
                        messages=[
                            {"role": "system", "content": self.system_prompt},
                            {"role": "user", "content": text}
                        ],
                        max_tokens=10,
                        temperature=0.1
                    )
                    
                    prediction = response.choices[0].message.content.strip().lower()
                    return prediction, True
                    
                except Exception as e2:
                    print(f"❌ Error con modelo base: {str(e2)}")
                    return "", False
            else:
                print(f"❌ Error en predicción: {error_msg}")
                return "", False
    
    def run_tests(self) -> Dict:
        """Ejecuta todas las pruebas y calcula métricas"""
        
        if not self.fine_tuned_model:
            print("❌ Error: Modelo no cargado")
            return {}
        
        test_cases = self.create_test_cases()
        results = []
        correct = 0
        
        print(f"🧪 Ejecutando {len(test_cases)} casos de prueba...")
        
        for i, case in enumerate(test_cases, 1):
            text = case["text"]
            expected = case["expected"]
            
            print(f"\n📝 Caso {i}: {text}")
            
            prediction, success = self.test_single_case(text)
            
            if success:
                is_correct = prediction == expected
                if is_correct:
                    correct += 1
                    print(f"✅ Predicción: {prediction} (Esperado: {expected})")
                else:
                    print(f"❌ Predicción: {prediction} (Esperado: {expected})")
                
                results.append({
                    "case_number": i,
                    "text": text,
                    "expected": expected,
                    "predicted": prediction,
                    "correct": is_correct
                })
            else:
                print(f"❌ Error en la predicción")
                results.append({
                    "case_number": i,
                    "text": text,
                    "expected": expected,
                    "predicted": "ERROR",
                    "correct": False
                })
        
        # Calcular métricas
        accuracy = correct / len(test_cases) if test_cases else 0
        
        summary = {
            "model_id": self.fine_tuned_model,
            "total_cases": len(test_cases),
            "correct_predictions": correct,
            "accuracy": accuracy,
            "test_results": results,
            "performance_by_intent": self._calculate_intent_metrics(results)
        }
        
        return summary
    
    def _calculate_intent_metrics(self, results: List[Dict]) -> Dict:
        """Calcula métricas por intención"""
        
        intent_stats = {}
        
        for result in results:
            if result["predicted"] == "ERROR":
                continue
                
            expected = result["expected"]
            if expected not in intent_stats:
                intent_stats[expected] = {"total": 0, "correct": 0}
            
            intent_stats[expected]["total"] += 1
            if result["correct"]:
                intent_stats[expected]["correct"] += 1
        
        # Calcular accuracy por intención
        for intent in intent_stats:
            total = intent_stats[intent]["total"]
            correct = intent_stats[intent]["correct"]
            intent_stats[intent]["accuracy"] = correct / total if total > 0 else 0
        
        return intent_stats
    
    def save_test_results(self, summary: Dict) -> None:
        """Guarda los resultados de las pruebas"""
        
        results_path = os.path.join(Config.RESULTS_PATH, "test_results.json")
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Resultados guardados en: {results_path}")
    
    def print_summary(self, summary: Dict) -> None:
        """Imprime resumen de resultados"""
        
        print(f"\n📊 RESUMEN DE PRUEBAS")
        print(f"{'='*50}")
        print(f"🤖 Modelo: {summary['model_id']}")
        print(f"📝 Casos totales: {summary['total_cases']}")
        print(f"✅ Predicciones correctas: {summary['correct_predictions']}")
        print(f"🎯 Accuracy general: {summary['accuracy']:.2%}")
        
        print(f"\n📈 RENDIMIENTO POR INTENCIÓN:")
        for intent, stats in summary['performance_by_intent'].items():
            print(f"   {intent.capitalize()}: {stats['correct']}/{stats['total']} ({stats['accuracy']:.2%})")

def main():
    """Función principal para ejecutar el Paso 7"""
    
    print("=== PASO 7: Probar el modelo ===")
    
    try:
        # Crear tester
        tester = ModelTester()
        
        # Cargar modelo
        if not tester.load_model_info():
            return
        
        # Ejecutar pruebas
        summary = tester.run_tests()
        
        if summary:
            # Guardar resultados
            tester.save_test_results(summary)
            
            # Mostrar resumen
            tester.print_summary(summary)
            
            print(f"\n✅ Paso 7 completado exitosamente")
            
            # Recomendaciones basadas en accuracy
            accuracy = summary['accuracy']
            if accuracy >= 0.9:
                print(f"🎉 Excelente rendimiento (≥90%). ¡El modelo está listo para producción!")
            elif accuracy >= 0.8:
                print(f"👍 Buen rendimiento (≥80%). Considera ajustes menores.")
            elif accuracy >= 0.7:
                print(f"⚠️ Rendimiento aceptable (≥70%). Revisa casos fallidos y considera más datos.")
            else:
                print(f"🔄 Rendimiento bajo (<70%). Revisa datos de entrenamiento y parámetros.")
        else:
            print(f"❌ No se pudieron ejecutar las pruebas")
            
    except Exception as e:
        print(f"❌ Error en pruebas: {str(e)}")

if __name__ == "__main__":
    main()