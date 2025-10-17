"""
Paso 5: Realizar Fine-Tuning con Azure OpenAI
"""

import json
import os
import sys
import time
from typing import Dict, Optional
from openai import AzureOpenAI

# Agregar el directorio padre al path para imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from config.config import Config

class FineTuningManager:
    """Gestiona el proceso de fine-tuning con Azure OpenAI"""
    
    def __init__(self):
        """Inicializa el cliente de Azure OpenAI"""
        
        if not Config.validate_config():
            raise ValueError("Configuración de Azure OpenAI incompleta. Revisa config.py")
        
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_KEY,
            api_version=Config.AZURE_OPENAI_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        
        self.training_file_id = None
        self.validation_file_id = None
        self.fine_tune_job_id = None
    
    def upload_training_files(self) -> bool:
        """Sube los archivos de entrenamiento y validación"""
        
        print("📤 Subiendo archivos de entrenamiento...")
        
        # Rutas de archivos
        train_path = os.path.join(Config.TRAINING_DATA_PATH, "train_data.jsonl")
        val_path = os.path.join(Config.VALIDATION_DATA_PATH, "validation_data.jsonl")
        
        if not os.path.exists(train_path) or not os.path.exists(val_path):
            print("❌ Error: Archivos de datos no encontrados")
            return False
        
        try:
            # Subir archivo de entrenamiento
            with open(train_path, 'rb') as f:
                training_file = self.client.files.create(
                    file=f,
                    purpose="fine-tune"
                )
            self.training_file_id = training_file.id
            print(f"✅ Archivo de entrenamiento subido: {self.training_file_id}")
            
            # Subir archivo de validación
            with open(val_path, 'rb') as f:
                validation_file = self.client.files.create(
                    file=f,
                    purpose="fine-tune"
                )
            self.validation_file_id = validation_file.id
            print(f"✅ Archivo de validación subido: {self.validation_file_id}")
            
            # Esperar a que los archivos se procesen
            print("⏳ Esperando a que los archivos se procesen...")
            if not self._wait_for_files_ready():
                print("❌ Error: Los archivos no se procesaron correctamente")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error subiendo archivos: {str(e)}")
            return False
    
    def _wait_for_files_ready(self) -> bool:
        """Espera a que los archivos estén listos para fine-tuning"""
        
        max_wait_time = 300  # 5 minutos máximo
        check_interval = 10  # Revisar cada 10 segundos
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            try:
                # Verificar archivo de entrenamiento
                train_file = self.client.files.retrieve(self.training_file_id)
                val_file = self.client.files.retrieve(self.validation_file_id)
                
                if train_file.status == "processed" and val_file.status == "processed":
                    print("✅ Archivos procesados y listos")
                    return True
                elif train_file.status == "error" or val_file.status == "error":
                    print("❌ Error procesando archivos")
                    return False
                else:
                    print(f"⏳ Procesando... ({elapsed_time}s)")
                    time.sleep(check_interval)
                    elapsed_time += check_interval
                    
            except Exception as e:
                print(f"❌ Error verificando archivos: {str(e)}")
                return False
        
        print("❌ Timeout esperando archivos")
        return False
    
    def start_fine_tuning(self) -> bool:
        """Inicia el proceso de fine-tuning"""
        
        if not self.training_file_id:
            print("❌ Error: Primero debes subir los archivos de entrenamiento")
            return False
        
        print("🚀 Iniciando fine-tuning...")
        
        try:
            # Crear job de fine-tuning
            fine_tune_job = self.client.fine_tuning.jobs.create(
                training_file=self.training_file_id,
                validation_file=self.validation_file_id,
                model=Config.BASE_MODEL,
                hyperparameters={
                    "n_epochs": Config.FINE_TUNING_PARAMS["n_epochs"],
                    "batch_size": Config.FINE_TUNING_PARAMS["batch_size"],
                    "learning_rate_multiplier": Config.FINE_TUNING_PARAMS["learning_rate_multiplier"]
                }
            )
            
            self.fine_tune_job_id = fine_tune_job.id
            print(f"✅ Fine-tuning iniciado. Job ID: {self.fine_tune_job_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando fine-tuning: {str(e)}")
            return False
    
    def monitor_fine_tuning(self) -> Optional[str]:
        """Monitorea el progreso del fine-tuning"""
        
        if not self.fine_tune_job_id:
            print("❌ Error: No hay un job de fine-tuning activo")
            return None
        
        print(f"👀 Monitoreando fine-tuning job: {self.fine_tune_job_id}")
        
        try:
            while True:
                # Obtener estado del job
                job = self.client.fine_tuning.jobs.retrieve(self.fine_tune_job_id)
                status = job.status
                
                print(f"📊 Estado: {status}")
                
                if status == "succeeded":
                    print(f"🎉 Fine-tuning completado exitosamente!")
                    print(f"🤖 Modelo fine-tuned: {job.fine_tuned_model}")
                    return job.fine_tuned_model
                
                elif status == "failed":
                    print(f"❌ Fine-tuning falló")
                    if hasattr(job, 'error'):
                        print(f"   Error: {job.error}")
                    return None
                
                elif status in ["pending", "running"]:
                    print(f"⏳ En progreso... Esperando 30 segundos")
                    time.sleep(30)
                
                else:
                    print(f"❓ Estado desconocido: {status}")
                    time.sleep(30)
                    
        except KeyboardInterrupt:
            print(f"\n⏸️ Monitoreo interrumpido. Job ID: {self.fine_tune_job_id}")
            return None
        except Exception as e:
            print(f"❌ Error monitoreando: {str(e)}")
            return None
    
    def save_fine_tuning_info(self, model_id: Optional[str]) -> None:
        """Guarda información del fine-tuning"""
        
        info = {
            "training_file_id": self.training_file_id,
            "validation_file_id": self.validation_file_id,
            "fine_tune_job_id": self.fine_tune_job_id,
            "fine_tuned_model": model_id,
            "base_model": Config.BASE_MODEL,
            "hyperparameters": Config.FINE_TUNING_PARAMS,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        info_path = os.path.join(Config.RESULTS_PATH, "fine_tuning_info.json")
        os.makedirs(os.path.dirname(info_path), exist_ok=True)
        
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Información guardada en: {info_path}")

def main():
    """Función principal para ejecutar el Paso 5"""
    
    print("=== PASO 5: Realizar Fine-Tuning ===")
    
    # Verificar configuración
    if not Config.validate_config():
        print("❌ Error: Configuración de Azure OpenAI incompleta")
        print("   Completa las variables AZURE_OPENAI_ENDPOINT y AZURE_OPENAI_KEY en config.py")
        return
    
    try:
        # Crear manager de fine-tuning
        ft_manager = FineTuningManager()
        
        # Subir archivos
        if not ft_manager.upload_training_files():
            return
        
        # Iniciar fine-tuning
        if not ft_manager.start_fine_tuning():
            return
        
        # Monitorear progreso
        print("\n⏳ El fine-tuning puede tomar varios minutos...")
        model_id = ft_manager.monitor_fine_tuning()
        
        # Guardar información
        ft_manager.save_fine_tuning_info(model_id)
        
        if model_id:
            print(f"\n✅ Paso 5 completado exitosamente")
            print(f"🤖 Modelo fine-tuned disponible: {model_id}")
        else:
            print(f"\n❌ Fine-tuning no completado")
            
    except Exception as e:
        print(f"❌ Error en fine-tuning: {str(e)}")

if __name__ == "__main__":
    main()