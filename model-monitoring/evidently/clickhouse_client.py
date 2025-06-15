import pandas as pd
from clickhouse_driver import Client
from typing import Dict, Any
import logging

from config import Config

logger = logging.getLogger(__name__)

class ClickHouseClient:
    def __init__(self):
        self.client = Client(
            host=Config.CLICKHOUSE_HOST,
            port=Config.CLICKHOUSE_PORT,
            user=Config.CLICKHOUSE_USER,
            password=Config.CLICKHOUSE_PASSWORD,
            database=Config.CLICKHOUSE_DATABASE
        )
    
    def test_connection(self) -> bool:
        """Test connection to ClickHouse"""
        try:
            self.client.execute('SELECT 1')
            return True
        except Exception as e:
            logger.error(f"ClickHouse connection error: {e}")
            return False
    
    def get_yolo_predictions_data(self, hours_ago: int = None, limit: int = None) -> pd.DataFrame:
        """
        Extract YOLO prediction data from otel_traces
        
        Args:
            hours_ago: Get data older than N hours ago
            limit: Limit the number of records (for current dataset)
        """
        # Full table name with database
        table_name = f"{Config.CLICKHOUSE_DATABASE}.{Config.CLICKHOUSE_TABLE}"
        
        query = f"""
        SELECT 
            Timestamp,
            SpanAttributes['prediction_id'] as prediction_id,
            SpanAttributes['processing_time_seconds'] as processing_time,
            SpanAttributes['filename'] as filename,
            SpanAttributes['model_name'] as model_name,
            arrayJoin(Events.Attributes)['class_name'] as class_name,
            arrayJoin(Events.Attributes)['confidence'] as confidence,
            arrayJoin(Events.Attributes)['object_index'] as object_index
        FROM {table_name}
        WHERE SpanName = 'yolo_prediction'
        """
        
        # Add time condition if specified
        if hours_ago:
            query += f" AND Timestamp <= now() - INTERVAL {hours_ago} HOUR"
            query += f" AND Timestamp >= now() - INTERVAL {hours_ago + 24} HOUR"  # For a day from the reference point
        
        # Sorting and limit
        query += " ORDER BY Timestamp DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            result = self.client.execute(query)
            
            # Create DataFrame
            columns = [
                'timestamp', 'prediction_id', 'processing_time', 
                'filename', 'model_name', 'class_name', 'confidence', 'object_index'
            ]
            
            df = pd.DataFrame(result, columns=columns)
            
            # Convert data types
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce')
            df['processing_time'] = pd.to_numeric(df['processing_time'], errors='coerce')
            df['object_index'] = pd.to_numeric(df['object_index'], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"ClickHouse query error: {e}")
            raise
    
    def get_reference_dataset(self) -> pd.DataFrame:
        """Get reference dataset (specific data with high confidence)"""
        # Full table name with database
        table_name = f"{Config.CLICKHOUSE_DATABASE}.{Config.CLICKHOUSE_TABLE}"
        
        query = f"""
        SELECT 
            Timestamp,
            SpanAttributes['prediction_id'] as prediction_id,
            SpanAttributes['processing_time_seconds'] as processing_time,
            SpanAttributes['filename'] as filename,
            SpanAttributes['model_name'] as model_name,
            arrayJoin(Events.Attributes)['class_name'] as class_name,
            arrayJoin(Events.Attributes)['confidence'] as confidence,
            arrayJoin(Events.Attributes)['object_index'] as object_index
        FROM {table_name}
        WHERE SpanName = 'yolo_prediction'
        ORDER BY Timestamp DESC
        """
        
        try:
            result = self.client.execute(query)
            
            # Create DataFrame
            columns = [
                'timestamp', 'prediction_id', 'processing_time', 
                'filename', 'model_name', 'class_name', 'confidence', 'object_index'
            ]
            
            df = pd.DataFrame(result, columns=columns)
            
            # Convert data types
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce')
                df['processing_time'] = pd.to_numeric(df['processing_time'], errors='coerce')
                df['object_index'] = pd.to_numeric(df['object_index'], errors='coerce')
                
                filtered_df = df[
                    (df['class_name'] == Config.REFERENCE_CLASS_NAME) & 
                    (df['confidence'] > Config.REFERENCE_MIN_CONFIDENCE)
                ].head(Config.REFERENCE_LIMIT)
                
                return filtered_df
            else:
                return df
            
        except Exception as e:
            logger.error(f"Reference dataset query error: {e}")
            raise
    
    def get_current_dataset(self) -> pd.DataFrame:
        """Get current dataset (predictions from the last N days)"""
        # Full table name with database
        table_name = f"{Config.CLICKHOUSE_DATABASE}.{Config.CLICKHOUSE_TABLE}"
        
        # Simplified query, like in the reference dataset
        query = f"""
        SELECT 
            Timestamp,
            SpanAttributes['prediction_id'] as prediction_id,
            SpanAttributes['processing_time_seconds'] as processing_time,
            SpanAttributes['filename'] as filename,
            SpanAttributes['model_name'] as model_name,
            arrayJoin(Events.Attributes)['class_name'] as class_name,
            arrayJoin(Events.Attributes)['confidence'] as confidence,
            arrayJoin(Events.Attributes)['object_index'] as object_index
        FROM {table_name}
        WHERE SpanName = 'yolo_prediction'
          AND Timestamp >= now() - INTERVAL {Config.CURRENT_DAYS_AGO} DAY
        ORDER BY Timestamp DESC
        """
        
        try:
            result = self.client.execute(query)
            
            # Create DataFrame
            columns = [
                'timestamp', 'prediction_id', 'processing_time', 
                'filename', 'model_name', 'class_name', 'confidence', 'object_index'
            ]
            
            df = pd.DataFrame(result, columns=columns)
            
            # Convert data types
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['confidence'] = pd.to_numeric(df['confidence'], errors='coerce')
                df['processing_time'] = pd.to_numeric(df['processing_time'], errors='coerce')
                df['object_index'] = pd.to_numeric(df['object_index'], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"Current dataset query error: {e}")
            raise
    
    def get_predictions_summary(self) -> Dict[str, Any]:
        """Get prediction summary statistics"""
        table_name = f"{Config.CLICKHOUSE_DATABASE}.{Config.CLICKHOUSE_TABLE}"
        
        query = f"""
        SELECT 
            count() as total_predictions,
            countDistinct(SpanAttributes['prediction_id']) as unique_predictions,
            min(Timestamp) as earliest_prediction,
            max(Timestamp) as latest_prediction,
            avg(SpanAttributes['processing_time_seconds']) as avg_processing_time
        FROM {table_name}
        WHERE SpanName = 'yolo_prediction'
        """
        
        try:
            result = self.client.execute(query)
            if result:
                row = result[0]
                return {
                    'total_predictions': row[0],
                    'unique_predictions': row[1], 
                    'earliest_prediction': row[2],
                    'latest_prediction': row[3],
                    'avg_processing_time': float(row[4]) if row[4] else 0
                }
        except Exception as e:
            logger.error(f"Error getting prediction summary statistics: {e}")
            return {}
    
    def get_class_distribution(self, hours_ago: int = None) -> pd.DataFrame:
        """Get object class distribution"""
        table_name = f"{Config.CLICKHOUSE_DATABASE}.{Config.CLICKHOUSE_TABLE}"
        
        query = f"""
        SELECT 
            arrayJoin(Events.Attributes)['class_name'] as class_name,
            count() as count,
            avg(arrayJoin(Events.Attributes)['confidence']) as avg_confidence
        FROM {table_name}
        WHERE SpanName = 'yolo_prediction'
        """
        
        if hours_ago:
            query += f" AND Timestamp >= now() - INTERVAL {hours_ago} HOUR"
        
        query += " GROUP BY class_name ORDER BY count DESC"
        
        try:
            result = self.client.execute(query)
            df = pd.DataFrame(result, columns=['class_name', 'count', 'avg_confidence'])
            return df
        except Exception as e:
            logger.error(f"Error getting class distribution: {e}")
            return pd.DataFrame() 