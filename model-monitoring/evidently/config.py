import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Evidently Cloud configuration
    EVIDENTLY_API_KEY = os.getenv('EVIDENTLY_API_KEY', '')
    EVIDENTLY_URL = os.getenv('EVIDENTLY_URL', 'https://app.evidently.cloud')
    EVIDENTLY_PROJECT_ID = os.getenv('EVIDENTLY_PROJECT_ID', '')
    EVIDENTLY_PROJECT_NAME = os.getenv('EVIDENTLY_PROJECT_NAME', '')
    
    # ClickHouse configuration
    CLICKHOUSE_HOST = os.getenv('CLICKHOUSE_HOST', 'localhost')
    CLICKHOUSE_PORT = int(os.getenv('CLICKHOUSE_PORT', '30900'))
    CLICKHOUSE_USER = os.getenv('CLICKHOUSE_USER', 'default')
    CLICKHOUSE_PASSWORD = os.getenv('CLICKHOUSE_PASSWORD', '')
    CLICKHOUSE_DATABASE = os.getenv('CLICKHOUSE_DATABASE', 'yolo_analytics')
    CLICKHOUSE_TABLE = os.getenv('CLICKHOUSE_TABLE', 'otel_traces')
    
    # Reference dataset configuration
    REFERENCE_CLASS_NAME = os.getenv('REFERENCE_CLASS_NAME', 'book')
    REFERENCE_MIN_CONFIDENCE = float(os.getenv('REFERENCE_MIN_CONFIDENCE', '0.8'))
    REFERENCE_LIMIT = int(os.getenv('REFERENCE_LIMIT', '10'))
    
    # Current dataset configuration
    CURRENT_DAYS_AGO = int(os.getenv('CURRENT_DAYS_AGO', '7'))
    
    # Drift analysis configuration
    REFERENCE_DATASET_ID = os.getenv('REFERENCE_DATASET_ID', '')

    @classmethod
    def validate(cls) -> list:
        """Validation of required settings"""
        errors = []
        
        if not cls.EVIDENTLY_API_KEY:
            errors.append("EVIDENTLY_API_KEY is required")
        
        if not cls.REFERENCE_DATASET_ID:
            errors.append("REFERENCE_DATASET_ID is required (run create_reference_dataset.py first)")
            
        if cls.REFERENCE_MIN_CONFIDENCE < 0 or cls.REFERENCE_MIN_CONFIDENCE > 1:
            errors.append("REFERENCE_MIN_CONFIDENCE must be between 0 and 1")
            
        if cls.REFERENCE_LIMIT <= 0:
            errors.append("REFERENCE_LIMIT must be positive")
            
        if cls.CURRENT_DAYS_AGO <= 0:
            errors.append("CURRENT_DAYS_AGO must be positive")
        
        return errors
    
    @classmethod
    def print_config(cls):
        """Prints current configuration"""
        print(f"📊 Config: CH={cls.CLICKHOUSE_HOST}:{cls.CLICKHOUSE_PORT} | "
              f"Days={cls.CURRENT_DAYS_AGO} | "
              f"Ref={cls.REFERENCE_DATASET_ID[:8]}... | "
              f"Key={'✅' if cls.EVIDENTLY_API_KEY else '❌'}") 
              