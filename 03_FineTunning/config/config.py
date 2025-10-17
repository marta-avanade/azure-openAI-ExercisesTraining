"""
Configuración para el ejercicio de Fine-Tuning
Incluye endpoints de Azure OpenAI y parámetros del modelo
"""

from pathlib import Path
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Cargar .env automáticamente (si existe)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
dotenv_path = PROJECT_ROOT / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    # also try parent workspace root
    load_dotenv()


class Config:
    """Configuración principal del proyecto"""
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_KEY: str = os.getenv("AZURE_OPENAI_KEY", "")
    AZURE_OPENAI_VERSION: str = os.getenv("AZURE_OPENAI_VERSION", "2024-12-01-preview")
    
    # Modelo (se puede definir en .env como AZURE_OPENAI_MODEL)
    BASE_MODEL: str = os.getenv("AZURE_OPENAI_MODEL", os.getenv("BASE_MODEL", "gpt-4o-mini"))
    
    # Deployment del modelo fine-tuned
    FINE_TUNED_MODEL_DEPLOYMENT: str = os.getenv("FINE_TUNED_MODEL_DEPLOYMENT", "")
    
    # Rutas de archivos (absolutas basadas en el directorio del proyecto)
    PROJECT_ROOT: Path = PROJECT_ROOT
    RAW_DATA_PATH: Path = PROJECT_ROOT / "data" / "raw"
    PROCESSED_DATA_PATH: Path = PROJECT_ROOT / "data" / "processed"
    TRAINING_DATA_PATH: Path = PROJECT_ROOT / "data" / "training"
    VALIDATION_DATA_PATH: Path = PROJECT_ROOT / "data" / "validation"
    RESULTS_PATH: Path = PROJECT_ROOT / "results"
    LOGS_PATH: Path = PROJECT_ROOT / "logs"

    # Asegurar que las carpetas existan
    for p in [RAW_DATA_PATH, PROCESSED_DATA_PATH, TRAINING_DATA_PATH, VALIDATION_DATA_PATH, RESULTS_PATH, LOGS_PATH]:
        try:
            p.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
    
    # Parámetros de fine-tuning
    FINE_TUNING_PARAMS: Dict[str, Any] = {
        "n_epochs": int(os.getenv("FINE_TUNING_EPOCHS", 3)),
        "batch_size": int(os.getenv("FINE_TUNING_BATCH_SIZE", 1)),
        "learning_rate_multiplier": float(os.getenv("FINE_TUNING_LR_MULT", 0.1)),
        "prompt_loss_weight": float(os.getenv("FINE_TUNING_PROMPT_LOSS_WEIGHT", 0.01))
    }
    
    # Intenciones de clasificación
    INTENT_CATEGORIES = [
        "comprar",
        "devolver", 
        "queja",
        "consulta"
    ]
    
    # Configuración de división de datos
    TRAIN_SPLIT: float = float(os.getenv("TRAIN_SPLIT", 0.8))
    VALIDATION_SPLIT: float = float(os.getenv("VALIDATION_SPLIT", 0.2))

    @classmethod
    def validate_config(cls) -> bool:
        """Valida que la configuración esté completa"""
        required_vars = [cls.AZURE_OPENAI_ENDPOINT, cls.AZURE_OPENAI_KEY]
        return all(bool(var) for var in required_vars)