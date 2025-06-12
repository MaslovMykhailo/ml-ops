#!/usr/bin/env python3
"""
Ray job submission script
Submits ray_job.py as a Ray task with file uploads
"""

import os
import ray
import yaml
import logging
from pathlib import Path
from datetime import datetime

# Reduce Ray logging verbosity
logging.getLogger("ray").setLevel(logging.WARNING)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded environment variables from .env")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Or set environment variables manually")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

def load_config(config_path="config.yaml"):
    """Loads configuration from YAML file"""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        print(f"⚠️  Could not load config file: {e}")
        return None

def check_required_files():
    """Checks if all required files exist"""
    required_files = ["train_yolo.py", "config.yaml", "requirements.txt", "ray_job.py"]
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files found")
    return True

def prepare_job_files():
    """Prepares files for Ray job"""
    files_to_upload = [
        "train_yolo.py",
        "config.yaml", 
        "requirements.txt",
        "ray_job.py"
    ]

    file_contents = {}
    for file_name in files_to_upload:
        if Path(file_name).exists():
            with open(file_name, 'r') as f:
                file_contents[file_name] = f.read()
            print(f"  ✅ Prepared {file_name}")
        else:
            print(f"  ❌ Missing {file_name}")
            return None
    return file_contents

@ray.remote
def run_ray_job(file_contents):
    """Runs ray_job.py on Ray worker with uploaded files"""
    import subprocess
    import sys
    import tempfile
    import os
    
    # Create temporary directory and write files
    temp_dir = tempfile.mkdtemp()
    os.chdir(temp_dir)
    
    # Write all files to worker
    for filename, content in file_contents.items():
        with open(filename, 'w') as f:
            f.write(content)
    
    # Environment variables are now set through runtime_env
    print("✅ Files uploaded and environment configured")
    
    # Run ray_job.py
    try:
        result = subprocess.run([sys.executable, "ray_job.py"], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ray_job.py failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main function"""
    print("🚀 Ray Task Submission for YOLO Training")
    print("=" * 40)
    
    # Ray cluster address
    ray_address = "ray://localhost:10001"  # Ray cluster address
    
    # Check required files
    if not check_required_files():
        return
    
    # Collect W&B environment variables
    wandb_env = {
        'WANDB_API_KEY': os.getenv('WANDB_API_KEY'),
        'WANDB_PROJECT': os.getenv('WANDB_PROJECT'),
        'WANDB_ENTITY': os.getenv('WANDB_ENTITY')
    }
    
    # Check W&B configuration (without showing values)
    print("🔑 W&B Environment Variables:")
    for key, value in wandb_env.items():
        if value:
            print(f"   ✅ {key} is set")
        else:
            print(f"   ⚠️  {key} not set")
    
    if not wandb_env['WANDB_API_KEY']:
        print("\n⚠️  WANDB_API_KEY is required!")
        print("   Set it with: export WANDB_API_KEY=your_key")
        print("   Or get it from: https://wandb.ai/authorize")
    
    # Initialize Ray
    try:
        if not ray.is_initialized():
            ray.init(address=ray_address)
            print(f"✅ Connected to Ray cluster at {ray_address}")
            print("-" * 40)  # Separator after Ray connection logs
    except Exception as e:
        print(f"❌ Cannot connect to Ray cluster at {ray_address}: {e}")
        print("   Make sure Ray cluster is running:")
        print("   ray start --head --dashboard-host=0.0.0.0 --dashboard-port=8265")
        return
    
    try:
        # Prepare files
        print("📁 Preparing files...")
        file_contents = prepare_job_files()
        if not file_contents:
            return
        
        # Submit job
        print("🚀 Submitting ray_job.py as Ray task...")
        
        # Load configuration to get base run name
        config = load_config()
        base_run_name = config.get('run_name', 'yolo-ray-training') if config else 'yolo-ray-training'
        
        # Generate dynamic run name with timestamp
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        run_name = f"{base_run_name}-{timestamp}"
        
        # Prepare runtime environment with W&B variables
        env_vars = {k: v for k, v in wandb_env.items() if v}  # Only non-empty values
        env_vars['WANDB_RUN_NAME'] = run_name  # Add dynamic run name
        
        runtime_env = {
            "env_vars": env_vars
        }
        
        print(f"📋 Runtime environment: {len(runtime_env['env_vars'])} variables")
        print(f"🏃 Run name: {run_name}")
        for key in runtime_env['env_vars'].keys():
            if key != 'WANDB_API_KEY':  # Don't show API key
                print(f"   - {key}")
            else:
                print(f"   - {key} (hidden)")
        
        if not runtime_env['env_vars']:
            print("⚠️  No environment variables to pass!")
            print("   Make sure .env file exists or variables are exported")
        
        # Submit task with runtime environment
        task = run_ray_job.options(runtime_env=runtime_env).remote(file_contents)
        
        # Wait for completion
        print("👀 Waiting for task completion...")
        success = ray.get(task)
        
        if success:
            print("🎉 Training completed successfully!")
            print("🌐 Check results at:")
            print("   - Ray Dashboard: http://localhost:8265")
            print("   - W&B Dashboard: https://wandb.ai")
        else:
            print("❌ Training failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        ray.shutdown()
        print("🔌 Ray connection closed")

if __name__ == "__main__":
    main() 