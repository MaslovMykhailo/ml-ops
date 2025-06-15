import pandas as pd
from evidently.ui.workspace import CloudWorkspace
from evidently import Dataset, DataDefinition, Report
from evidently.presets import DataDriftPreset
import logging
from typing import Any
from datetime import datetime

from config import Config

logger = logging.getLogger(__name__)

class EvidentlyClient:
    def __init__(self):
        if not Config.EVIDENTLY_API_KEY:
            raise ValueError("EVIDENTLY_API_KEY is required. Please set it in environment variables.")
        
        self.workspace = CloudWorkspace(
            token=Config.EVIDENTLY_API_KEY,
            url=Config.EVIDENTLY_URL
        )
        self.project = None
    
    def create_or_get_project(self) -> Any:
        """Create or get existing project"""
        try:
            # If specific PROJECT_ID is specified, use it
            if Config.EVIDENTLY_PROJECT_ID:
                self.project = self.workspace.get_project(Config.EVIDENTLY_PROJECT_ID)
                return self.project
            
            # Try to find existing project by name
            projects = self.workspace.list_projects()
            for project in projects:
                if project.name == Config.EVIDENTLY_PROJECT_NAME:
                    self.project = project
                    return project
            
            # Create new project if not found
            self.project = self.workspace.create_project(Config.EVIDENTLY_PROJECT_NAME)
            return self.project
            
        except Exception as e:
            logger.error(f"Error creating/getting project: {e}")
            raise
    
    def prepare_dataset_for_evidently(self, df: pd.DataFrame, dataset_name: str) -> Dataset:
        """
        Prepare DataFrame for working with Evidently
        
        Args:
            df: DataFrame with YOLO prediction data
            dataset_name: Dataset name
        """
        if df.empty:
            raise ValueError(f"DataFrame is empty for dataset: {dataset_name}")
        
        # Clean data
        df_clean = df.copy()
        df_clean = df_clean.dropna(subset=['class_name', 'confidence'])
        
        # Keep only basic features for YOLO drift analysis
        features_df = df_clean[['class_name', 'confidence', 'processing_time']]
        
        # Create Dataset for Evidently
        dataset = Dataset.from_pandas(pd.DataFrame(features_df))
        
        return dataset
    
    def upload_dataset(self, df: pd.DataFrame, dataset_name: str, description: str = "") -> str:
        """Upload dataset to Evidently Cloud"""
        if not self.project:
            raise ValueError("Project not initialized. Call create_or_get_project() first")
        
        try:
            # Prepare dataset
            dataset = self.prepare_dataset_for_evidently(df, dataset_name)
            
            # Upload to Cloud (using correct API)
            dataset_id = self.workspace.add_dataset(
                dataset=dataset,
                name=dataset_name,
                project_id=self.project.id,
                description=description or f"YOLO predictions dataset uploaded at {datetime.now()}"
            )
            
            return dataset_id
            
        except Exception as e:
            logger.error(f"Error uploading dataset '{dataset_name}': {e}")
            raise
    
    def download_dataset(self, dataset_id: str) -> pd.DataFrame:
        """Download dataset from Evidently Cloud"""
        try:
            # Download dataset
            dataset = self.workspace.load_dataset(dataset_id=dataset_id)
            
            # Convert to DataFrame
            df = dataset.as_dataframe()
            
            return df
            
        except Exception as e:
            logger.error(f"Error downloading dataset {dataset_id}: {e}")
            raise
    
    def create_and_upload_drift_report(self, reference_dataset_id: str, current_df: pd.DataFrame) -> str:
        """
        Create drift report using reference from Cloud and current data
        
        Args:
            reference_dataset_id: ID of reference dataset in Evidently Cloud
            current_df: Current data (sent with the report)
            
        Returns:
            Report URL in Evidently Cloud
        """
        try:
            # Create/get project
            self.create_or_get_project()
            
            # Download reference dataset from Cloud
            reference_df = self.download_dataset(reference_dataset_id)
            
            # Prepare datasets
            reference_dataset = self.prepare_dataset_for_evidently(reference_df, "reference")
            current_dataset = self.prepare_dataset_for_evidently(current_df, "current")
            
            # Create drift report with metadata
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report = Report(
                metrics=[DataDriftPreset()],
                tags=[
                    "yolo_monitoring",
                    f"reference_dataset:{reference_dataset_id}",
                    f"created:{timestamp}"
                ]
            )
            
            # Run analysis - get snapshot
            my_eval = report.run(current_data=current_dataset, reference_data=reference_dataset)
            
            # Upload snapshot to Evidently Cloud using correct API
            run_id = self.workspace.add_run(
                self.project.id, 
                my_eval,
                include_data=True
            )
            
            # Form URL for viewing the report
            report_url = f"{Config.EVIDENTLY_URL}/projects/{self.project.id}/reports/{run_id}"
            
            return report_url
            
        except Exception as e:
            logger.error(f"Error creating drift report: {e}")
            raise 