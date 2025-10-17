"""
Paso 8: Analizar resultados y sugerir mejoras
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

class ResultsAnalyzer:
    """Analiza los resultados del fine-tuning y sugiere mejoras"""
    
    def __init__(self):
        self.test_results = None
        self.fine_tuning_info = None
    
    def load_results(self) -> bool:
        """Carga los resultados de las pruebas y fine-tuning"""
        
        # Cargar resultados de pruebas
        test_path = os.path.join(Config.RESULTS_PATH, "test_results.json")
        if not os.path.exists(test_path):
            print(f"❌ Error: No se encontraron resultados de pruebas en {test_path}")
            return False
        
        with open(test_path, 'r', encoding='utf-8') as f:
            self.test_results = json.load(f)
        
        # Cargar información de fine-tuning
        ft_path = os.path.join(Config.RESULTS_PATH, "fine_tuning_info.json")
        if os.path.exists(ft_path):
            with open(ft_path, 'r', encoding='utf-8') as f:
                self.fine_tuning_info = json.load(f)
        
        print("📂 Resultados cargados exitosamente")
        return True
    
    def analyze_accuracy_patterns(self) -> Dict:
        """Analiza patrones en la accuracy"""
        
        results = self.test_results["test_results"]
        intent_performance = self.test_results["performance_by_intent"]
        
        analysis = {
            "overall_accuracy": self.test_results["accuracy"],
            "best_performing_intent": None,
            "worst_performing_intent": None,
            "accuracy_distribution": intent_performance,
            "failed_cases": [],
            "patterns": []
        }
        
        # Encontrar mejor y peor intención
        best_intent = max(intent_performance.items(), key=lambda x: x[1]["accuracy"])
        worst_intent = min(intent_performance.items(), key=lambda x: x[1]["accuracy"])
        
        analysis["best_performing_intent"] = {
            "intent": best_intent[0],
            "accuracy": best_intent[1]["accuracy"]
        }
        analysis["worst_performing_intent"] = {
            "intent": worst_intent[0], 
            "accuracy": worst_intent[1]["accuracy"]
        }
        
        # Analizar casos fallidos
        for result in results:
            if not result["correct"] and result["predicted"] != "ERROR":
                analysis["failed_cases"].append({
                    "text": result["text"],
                    "expected": result["expected"],
                    "predicted": result["predicted"],
                    "case_number": result["case_number"]
                })
        
        # Identificar patrones
        if analysis["overall_accuracy"] < 0.8:
            analysis["patterns"].append("Accuracy general baja - necesita más datos de entrenamiento")
        
        accuracy_variance = max(intent_performance.values(), key=lambda x: x["accuracy"])["accuracy"] - \
                          min(intent_performance.values(), key=lambda x: x["accuracy"])["accuracy"]
        
        if accuracy_variance > 0.3:
            analysis["patterns"].append("Gran varianza entre intenciones - datos desbalanceados")
        
        if len(analysis["failed_cases"]) > 0:
            confusion_pairs = {}
            for case in analysis["failed_cases"]:
                pair = f"{case['expected']} -> {case['predicted']}"
                confusion_pairs[pair] = confusion_pairs.get(pair, 0) + 1
            
            most_common_confusion = max(confusion_pairs.items(), key=lambda x: x[1])
            analysis["patterns"].append(f"Confusión más común: {most_common_confusion[0]} ({most_common_confusion[1]} casos)")
        
        return analysis
    
    def generate_improvement_suggestions(self, analysis: Dict) -> List[str]:
        """Genera sugerencias de mejora basadas en el análisis"""
        
        suggestions = []
        accuracy = analysis["overall_accuracy"]
        
        # Sugerencias basadas en accuracy general
        if accuracy < 0.7:
            suggestions.append("🔄 CRÍTICO: Accuracy muy baja (<70%). Considera:")
            suggestions.append("   • Aumentar significativamente los datos de entrenamiento")
            suggestions.append("   • Revisar la calidad y coherencia de las etiquetas")
            suggestions.append("   • Simplificar las categorías o mejorar las definiciones")
            
        elif accuracy < 0.8:
            suggestions.append("⚠️ MEJORABLE: Accuracy moderada (70-80%). Considera:")
            suggestions.append("   • Agregar más ejemplos de entrenamiento")
            suggestions.append("   • Mejorar la diversidad de frases en cada categoría")
            suggestions.append("   • Revisar casos ambiguos o mal etiquetados")
        
        # Sugerencias basadas en balance entre intenciones
        worst_intent = analysis["worst_performing_intent"]
        best_intent = analysis["best_performing_intent"]
        
        if best_intent["accuracy"] - worst_intent["accuracy"] > 0.3:
            suggestions.append(f"⚖️ DESBALANCE: '{worst_intent['intent']}' tiene accuracy muy baja ({worst_intent['accuracy']:.1%})")
            suggestions.append(f"   • Agregar más ejemplos diversos para '{worst_intent['intent']}'")
            suggestions.append(f"   • Revisar si las definiciones de '{worst_intent['intent']}' son claras")
        
        # Sugerencias basadas en casos fallidos
        if analysis["failed_cases"]:
            suggestions.append(f"🔍 CASOS FALLIDOS: {len(analysis['failed_cases'])} casos necesitan atención:")
            
            # Mostrar algunos ejemplos problemáticos
            for i, case in enumerate(analysis["failed_cases"][:3]):
                suggestions.append(f"   • '{case['text']}' → predijo '{case['predicted']}' (esperado '{case['expected']}')")
            
            if len(analysis["failed_cases"]) > 3:
                suggestions.append(f"   • ... y {len(analysis['failed_cases']) - 3} casos más")
        
        # Sugerencias de hiperparámetros
        if self.fine_tuning_info:
            suggestions.append("🎛️ HIPERPARÁMETROS: Considera ajustar:")
            
            current_epochs = self.fine_tuning_info["hyperparameters"]["n_epochs"]
            if accuracy < 0.8 and current_epochs < 5:
                suggestions.append(f"   • Aumentar epochs de {current_epochs} a 4-6")
            
            if accuracy > 0.95:
                suggestions.append("   • Posible overfitting - reducir epochs o agregar regularización")
        
        return suggestions
    
    def create_improvement_report(self) -> Dict:
        """Crea un reporte completo de mejoras"""
        
        analysis = self.analyze_accuracy_patterns()
        suggestions = self.generate_improvement_suggestions(analysis)
        
        report = {
            "model_performance": {
                "overall_accuracy": analysis["overall_accuracy"],
                "performance_grade": self._get_performance_grade(analysis["overall_accuracy"]),
                "intent_performance": analysis["accuracy_distribution"]
            },
            "analysis": analysis,
            "improvement_suggestions": suggestions,
            "next_steps": self._get_next_steps(analysis["overall_accuracy"]),
            "data_recommendations": self._get_data_recommendations(analysis)
        }
        
        return report
    
    def _get_performance_grade(self, accuracy: float) -> str:
        """Asigna una calificación al rendimiento"""
        
        if accuracy >= 0.95:
            return "EXCELENTE (A+)"
        elif accuracy >= 0.9:
            return "EXCELENTE (A)"
        elif accuracy >= 0.8:
            return "BUENO (B)"
        elif accuracy >= 0.7:
            return "ACEPTABLE (C)"
        elif accuracy >= 0.6:
            return "DEFICIENTE (D)"
        else:
            return "MUY DEFICIENTE (F)"
    
    def _get_next_steps(self, accuracy: float) -> List[str]:
        """Define próximos pasos basados en el rendimiento"""
        
        if accuracy >= 0.9:
            return [
                "✅ El modelo está listo para producción",
                "🔄 Monitorear rendimiento en datos reales",
                "📈 Considerar A/B testing con modelo base"
            ]
        elif accuracy >= 0.8:
            return [
                "🔧 Hacer ajustes menores antes de producción",
                "📊 Recolectar más datos de las intenciones problemáticas",
                "🧪 Probar con datos de validación adicionales"
            ]
        else:
            return [
                "🛠️ Requiere trabajo adicional antes de despliegue",
                "📈 Aumentar dataset de entrenamiento",
                "🔄 Repetir proceso de fine-tuning con mejoras"
            ]
    
    def _get_data_recommendations(self, analysis: Dict) -> Dict:
        """Recomienda mejoras específicas en los datos"""
        
        recommendations = {
            "quantity": {
                "current_examples_per_intent": 3,
                "recommended_minimum": 10,
                "recommended_optimal": 20
            },
            "quality": [
                "Aumentar diversidad léxica en cada categoría",
                "Incluir casos ambiguos para mejorar robustez",
                "Agregar variaciones de longitud de texto"
            ],
            "balance": []
        }
        
        # Recomendaciones de balance
        worst_intent = analysis["worst_performing_intent"]
        if worst_intent["accuracy"] < 0.8:
            recommendations["balance"].append(f"Priorizar ejemplos adicionales para '{worst_intent['intent']}'")
        
        return recommendations
    
    def save_analysis_report(self, report: Dict) -> None:
        """Guarda el reporte de análisis"""
        
        report_path = os.path.join(Config.RESULTS_PATH, "improvement_analysis.json")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Reporte de análisis guardado en: {report_path}")
    
    def print_analysis_summary(self, report: Dict) -> None:
        """Imprime resumen del análisis"""
        
        performance = report["model_performance"]
        
        print(f"\n📋 ANÁLISIS DE RESULTADOS")
        print(f"{'='*60}")
        print(f"🎯 Accuracy general: {performance['overall_accuracy']:.2%}")
        print(f"📊 Calificación: {performance['performance_grade']}")
        
        print(f"\n📈 RENDIMIENTO POR INTENCIÓN:")
        for intent, stats in performance["intent_performance"].items():
            print(f"   {intent.capitalize()}: {stats['accuracy']:.2%} ({stats['correct']}/{stats['total']})")
        
        print(f"\n💡 SUGERENCIAS DE MEJORA:")
        for suggestion in report["improvement_suggestions"]:
            print(f"   {suggestion}")
        
        print(f"\n🎯 PRÓXIMOS PASOS:")
        for step in report["next_steps"]:
            print(f"   {step}")

def main():
    """Función principal para ejecutar el Paso 8"""
    
    print("=== PASO 8: Analizar resultados y mejorar ===")
    
    try:
        # Crear analizador
        analyzer = ResultsAnalyzer()
        
        # Cargar resultados
        if not analyzer.load_results():
            return
        
        # Crear reporte de análisis
        report = analyzer.create_improvement_report()
        
        # Guardar reporte
        analyzer.save_analysis_report(report)
        
        # Mostrar resumen
        analyzer.print_analysis_summary(report)
        
        print(f"\n✅ Paso 8 completado exitosamente")
        print(f"📁 Reporte completo disponible en: {Config.RESULTS_PATH}")
        
    except Exception as e:
        print(f"❌ Error en análisis: {str(e)}")

if __name__ == "__main__":
    main()