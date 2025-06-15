import logging
import sys
from datetime import datetime

from clickhouse_client import ClickHouseClient
from evidently_client import EvidentlyClient
from config import Config

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    """Main function"""
    print("🔧 Creating Reference Dataset")
    print("=" * 30)
    
    # Configuration validation
    errors = []
    if not Config.EVIDENTLY_API_KEY:
        errors.append("EVIDENTLY_API_KEY is required")
    if Config.REFERENCE_MIN_CONFIDENCE < 0 or Config.REFERENCE_MIN_CONFIDENCE > 1:
        errors.append("REFERENCE_MIN_CONFIDENCE must be between 0 and 1")
    if Config.REFERENCE_LIMIT <= 0:
        errors.append("REFERENCE_LIMIT must be positive")
        
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"   • {error}")
        sys.exit(1)
    
    try:
        # Create clients
        ch_client = ClickHouseClient()
        ev_client = EvidentlyClient()
        
        # Check ClickHouse connection
        if not ch_client.test_connection():
            raise Exception("ClickHouse connection failed")
        
        # Get reference data
        logger.info("Fetching reference data from ClickHouse...")
        reference_df = ch_client.get_reference_dataset()
        
        if reference_df.empty:
            raise Exception(f"No reference data found. Need {Config.REFERENCE_LIMIT} records with "
                          f"class='{Config.REFERENCE_CLASS_NAME}' and confidence > {Config.REFERENCE_MIN_CONFIDENCE}")
        
        # Create/get project in Evidently
        project = ev_client.create_or_get_project()
        
        # Upload reference dataset
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dataset_name = f"Reference Dataset {timestamp}"
        description = (f"Reference dataset: {Config.REFERENCE_LIMIT} {Config.REFERENCE_CLASS_NAME} "
                      f"objects with confidence > {Config.REFERENCE_MIN_CONFIDENCE}. "
                      f"Created: {datetime.now().isoformat()}")
        
        logger.info(f"Uploading reference dataset to Evidently Cloud...")
        dataset_id = ev_client.upload_dataset(reference_df, dataset_name, description)
        
        print("✅ Reference dataset created!")
        print(f"📊 Dataset ID: {dataset_id}")
        print(f"💡 Set: export REFERENCE_DATASET_ID={dataset_id}")
        
        return dataset_id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Failed to create reference dataset: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 