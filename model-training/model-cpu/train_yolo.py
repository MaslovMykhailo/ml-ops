#!/usr/bin/env python3
"""
YOLOv8n training script with Weights & Biases integration
Trains YOLOv8n model on CPU with full W&B tracking and model saving
Uses built-in YOLO W&B integration
"""

import os
import yaml
import wandb
from pathlib import Path
from dotenv import load_dotenv
from ultralytics import YOLO
import torch

def load_config(config_path="config.yaml"):
    """Loads configuration from YAML file"""
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def setup_wandb_environment():
    """Sets up W&B environment and enables YOLO W&B integration"""
    # Load environment variables
    load_dotenv()
    
    # Get W&B API key from environment
    wandb_api_key = os.getenv('WANDB_API_KEY')
    if not wandb_api_key:
        print("Warning: WANDB_API_KEY not found in environment variables")
        print("Please set your W&B API key in .env file")
        return False
    
    # Login to W&B
    try:
        wandb.login(key=wandb_api_key)
        print("✅ Successfully logged in to W&B")
        
        # Enable W&B logging in YOLO settings
        from ultralytics.utils import SETTINGS
        SETTINGS['wandb'] = True
        print("✅ W&B logging enabled in YOLO settings")
        
        return True
    except Exception as e:
        print(f"❌ Failed to setup W&B: {e}")
        return False

def train_model(config):
    """Trains YOLOv8n model with built-in W&B tracking"""
    
    # Override run_name with environment variable if set
    run_name = os.getenv('WANDB_RUN_NAME', config['run_name'])
    
    print("🚀 Starting YOLOv8n training on CPU...")
    print(f"📊 W&B Project: {config['wandb_project']}")
    print(f"🏃 Run Name: {run_name}")
    
    # Initialize model
    model = YOLO(config['model'])
    
    # Training parameters - YOLO will automatically handle W&B integration
    train_args = {
        'data': config['data'],
        'epochs': config['epochs'],
        'batch': config['batch'],
        'imgsz': config['imgsz'],
        'device': config['device'],
        'workers': config['workers'],
        'optimizer': config['optimizer'],
        'lr0': config['lr0'],
        'momentum': config['momentum'],
        'weight_decay': config['weight_decay'],
        'save': config['save'],
        'save_period': config['save_period'],
        'project': config['wandb_project'],  # W&B project name
        'name': run_name,                    # W&B run name (dynamic)
        'plots': True,
        'verbose': True
    }
    
    print(f"🔧 Training parameters: {train_args}")
    
    # Start training - YOLO will automatically log to W&B
    results = model.train(**train_args)
    
    print("✅ Training completed with built-in W&B logging!")
    
    return model, results

def main():
    """Main training function"""
    print("=" * 60)
    print("🤖 YOLOv8n CPU Training with W&B Integration")
    print("=" * 60)
    
    # Check if we're running on CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🖥️  Device: {device}")
    
    try:
        # Load configuration
        config = load_config()
        
        # Force CPU usage as specified in requirements
        config['device'] = 'cpu'
        
        # Set up W&B environment (login and enable YOLO integration)
        if not setup_wandb_environment():
            print("⚠️  Continuing without W&B logging")
        
        # Train model with built-in W&B integration
        model, results = train_model(config)
        
        # Get final run name (may be overridden by environment)
        final_run_name = os.getenv('WANDB_RUN_NAME', config['run_name'])
        
        print("✅ Training completed successfully!")
        print(f"📁 Results saved in: {config['wandb_project']}/{final_run_name}/")
        print(f"🌐 Check your W&B dashboard at: https://wandb.ai")
        
    except Exception as e:
        print(f"❌ Error during training: {str(e)}")
        raise

if __name__ == "__main__":
    main() 