"""
Paso 6: Verificar el estado del deployment del modelo fine-tuned
"""

import json
import os
import sys
import time
from typing import Optional, Dict
from openai import AzureOpenAI

# Agregar el directorio padre al path para imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from config.config import Config

class ModelDeployment:
    """Verifica el estado del deployment del modelo fine-tuned"""
    
    def __init__(self):
        """Inicializa el cliente de Azure OpenAI"""
        
        if not Config.validate_config():
            raise ValueError("Configuración de Azure OpenAI incompleta")
        
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_KEY,
            api_version=Config.AZURE_OPENAI_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        
        self.fine_tuned_model = None
    
    def load_fine_tuned_model_info(self) -> bool:
        """Carga información del modelo fine-tuned"""
        
        info_path = os.path.join(Config.RESULTS_PATH, "fine_tuning_info.json")
        
        if not os.path.exists(info_path):
            print(f"❌ Error: No se encontró información de fine-tuning en {info_path}")
            print("   Ejecuta primero el Paso 5")
            return False
        
        with open(info_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
        
        self.fine_tuned_model = info.get("fine_tuned_model")
        
        if not self.fine_tuned_model:
            print("❌ Error: No se encontró ID del modelo fine-tuned")
            return False
        
        print(f"📂 Modelo fine-tuned cargado: {self.fine_tuned_model}")
        return True
    
    def check_deployment_status(self) -> Dict:
        """Verifica el estado del deployment del modelo fine-tuned"""
        
        print("🔍 Verificando estado del deployment...")
        
        try:
            # Lista todos los deployments para buscar nuestro modelo
            deployments = self.client.deployments.list()
            
            model_deployments = []
            for deployment in deployments.data:
                if deployment.model == self.fine_tuned_model:
                    model_deployments.append({
                        "id": deployment.id,
                        "status": deployment.status,
                        "model": deployment.model,
                        "created_at": deployment.created_at,
                        "scale_settings": deployment.scale_settings
                    })
            
            if model_deployments:
                print(f"✅ Encontrados {len(model_deployments)} deployment(s) para el modelo")
                for i, deploy in enumerate(model_deployments, 1):
                    print(f"   Deployment {i}:")
                    print(f"     - ID: {deploy['id']}")
                    print(f"     - Estado: {deploy['status']}")
                    print(f"     - Modelo: {deploy['model']}")
                    
                    if deploy['status'] == 'succeeded':
                        print(f"     - ✅ LISTO PARA USAR")
                    elif deploy['status'] in ['creating', 'pending']:
                        print(f"     - ⏳ EN PROCESO...")
                    else:
                        print(f"     - ⚠️ Estado: {deploy['status']}")
                
                return {
                    "found": True,
                    "deployments": model_deployments,
                    "ready": any(d['status'] == 'succeeded' for d in model_deployments)
                }
            else:
                print("❌ No se encontraron deployments para este modelo")
                print("   Verifica que el deployment esté creado en Azure Portal")
                return {"found": False, "deployments": [], "ready": False}
                
        except Exception as e:
            print(f"⚠️ Error verificando deployments: {str(e)}")
            print("   Esto puede ser normal si el deployment está en Azure Portal")
            return {"found": False, "deployments": [], "ready": False, "error": str(e)}

    def test_model_availability(self) -> bool:
        """Verifica que el modelo fine-tuned esté disponible"""
        
        print("🔍 Verificando que el modelo fine-tuned esté listo...")
        
        try:
            # Verificar que el modelo existe en la lista de fine-tuned models
            # Extraer el job ID del nombre del modelo
            if ".ft-" in self.fine_tuned_model:
                job_id_part = self.fine_tuned_model.split(".ft-")[1]
                print(f"🔧 ID del fine-tuning: ft-{job_id_part}")
                
                # Verificar el estado del job de fine-tuning
                job_id = f"ftjob-{job_id_part}"
                try:
                    job = self.client.fine_tuning.jobs.retrieve(job_id)
                    
                    if job.status == "succeeded" and job.fine_tuned_model:
                        print("✅ Modelo fine-tuned verificado y completado")
                        print(f"🎯 Modelo final: {job.fine_tuned_model}")
                        
                        # Actualizar con el nombre correcto del modelo si es diferente
                        if job.fine_tuned_model != self.fine_tuned_model:
                            print(f"🔄 Actualizando ID del modelo: {job.fine_tuned_model}")
                            self.fine_tuned_model = job.fine_tuned_model
                        
                        return True
                    else:
                        print(f"❌ El job de fine-tuning no ha completado exitosamente (estado: {job.status})")
                        return False
                        
                except Exception as job_error:
                    print(f"⚠️ No se pudo verificar el job: {str(job_error)}")
                    print(f"📝 Modelo a verificar: {self.fine_tuned_model}")
                    return True
            else:
                print("⚠️ Formato de modelo fine-tuned no reconocido, asumiendo que está disponible")
                return True
                
        except Exception as e:
            print(f"⚠️ Error verificando modelo: {str(e)}")
            print("📝 Continuando con el modelo especificado...")
            return True
    
    def create_deployment_info(self) -> Dict:
        """Crea información de despliegue"""
        
        deployment_info = {
            "model_id": self.fine_tuned_model,
            "status": "deployed",
            "endpoint": Config.AZURE_OPENAI_ENDPOINT,
            "api_version": Config.AZURE_OPENAI_VERSION,
            "usage_instructions": {
                "model_parameter": self.fine_tuned_model,
                "required_headers": [
                    "api-key: YOUR_API_KEY",
                    "Content-Type: application/json"
                ],
                "example_request": {
                    "model": self.fine_tuned_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Eres un asistente especializado en clasificar intenciones de clientes en una tienda."
                        },
                        {
                            "role": "user",
                            "content": "Quiero comprar una camiseta"
                        }
                    ]
                }
            }
        }
        
        return deployment_info
    
    def save_deployment_info(self, deployment_info: Dict) -> None:
        """Guarda información de despliegue"""
        
        deploy_path = os.path.join(Config.RESULTS_PATH, "deployment_info.json")
        
        with open(deploy_path, 'w', encoding='utf-8') as f:
            json.dump(deployment_info, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Información de despliegue guardada en: {deploy_path}")

def main():
    """Función principal para ejecutar el Paso 6"""
    
    print("=== PASO 6: Verificar estado del deployment ===")
    
    try:
        # Crear deployment manager
        deployment = ModelDeployment()
        
        # Cargar información del modelo
        if not deployment.load_fine_tuned_model_info():
            return
        
        # Verificar que el modelo fine-tuned esté disponible
        if not deployment.test_model_availability():
            print("❌ El modelo fine-tuned no está disponible")
            return
        
        # Verificar estado del deployment
        deployment_status = deployment.check_deployment_status()
        
        # Crear información de deployment independientemente del estado
        deployment_info = deployment.create_deployment_info()
        
        # Actualizar con información real del deployment si se encontró
        if deployment_status["found"] and deployment_status["deployments"]:
            active_deployment = None
            for deploy in deployment_status["deployments"]:
                if deploy["status"] == "succeeded":
                    active_deployment = deploy
                    break
            
            if active_deployment:
                deployment_info["deployment_id"] = active_deployment["id"]
                deployment_info["deployment_status"] = active_deployment["status"]
                deployment_info["ready"] = True
            else:
                deployment_info["deployment_status"] = "creating"
                deployment_info["ready"] = False
        else:
            deployment_info["deployment_status"] = "unknown"
            deployment_info["ready"] = False
        
        # Guardar información
        deployment.save_deployment_info(deployment_info)
        
        # Mostrar resumen final
        print(f"\n=== RESUMEN DEL PASO 6 ===")
        print(f"🔧 Modelo fine-tuned: {deployment.fine_tuned_model}")
        print(f"📍 Endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
        
        if deployment_status["ready"]:
            print(f"✅ Estado del deployment: LISTO PARA USAR")
            print(f"� El modelo está disponible para testing en el Paso 7")
        elif deployment_status["found"]:
            print(f"⏳ Estado del deployment: EN PROCESO")
            print(f"   Espera a que cambie a 'running' en Azure Portal")
        else:
            print(f"⚠️ Estado del deployment: NO DETECTADO")
            print(f"   Verifica el deployment en Azure Portal")
        
    except Exception as e:
        print(f"❌ Error verificando deployment: {str(e)}")

if __name__ == "__main__":
    main()