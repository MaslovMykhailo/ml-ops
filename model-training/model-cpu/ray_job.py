#!/usr/bin/env python3
"""
Ray job script for YOLO training
This script runs as a Ray job on the cluster
"""

import os
import sys
import subprocess
from pathlib import Path

def install_system_dependencies():
    """Installs system dependencies required for OpenCV"""
    print("🔧 Installing system dependencies...")
    try:
        # Check if we have sudo access and if apt is available
        result = subprocess.run(["which", "apt"], capture_output=True)
        if result.returncode != 0:
            print("⚠️  apt not found, skipping system dependencies")
            return True
        
        # Install libgl1 and other OpenCV dependencies
        result = subprocess.run(
            "sudo apt update && sudo apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1",
            shell=True, capture_output=True, text=True, check=True
        )
        print("✅ System dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Failed to install system dependencies: {e}")
        print("   This might cause OpenCV issues, but continuing...")
        print(f"   STDERR: {e.stderr}")
        return True  # Continue anyway as this might not be critical
    except Exception as e:
        print(f"⚠️  Error installing system dependencies: {e}")
        return True  # Continue anyway

def install_requirements():
    """Installs Python requirements on the worker"""
    print("📦 Installing Python requirements...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "config", "--user", "set", "global.index-url", "https://pypi.org/simple/"
        ])
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        print("✅ Python requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python requirements: {e}")
        print(f"STDERR: {e.stderr}")
        return False

def setup_environment():
    """Sets up environment variables on the worker"""
    wandb_key = os.getenv('WANDB_API_KEY')
    if wandb_key:
        print("✅ WANDB_API_KEY found in environment")
    else:
        print("⚠️  WANDB_API_KEY not found - W&B logging may not work")
    
    # Create .env file for training script
    with open('.env', 'w') as f:
        f.write(f"WANDB_API_KEY={wandb_key or ''}")
    print("✅ Environment file created")
    return True

def run_yolo_training():
    """Runs YOLO training on the worker"""
    print("🚀 Starting YOLO training...")
    try:
        # Run training with real-time output
        process = subprocess.Popen(
            [sys.executable, "train_yolo.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Display output in real-time
        for line in process.stdout:
            print(line.strip())
        
        process.wait()
        
        if process.returncode == 0:
            print("✅ Training completed successfully")
            return True
        else:
            print(f"❌ Training failed with return code: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return False

def main():
    """Main function - runs as a Ray job"""
    print("=" * 50)
    print("🤖 Ray Job: YOLO Training")
    print("=" * 50)
    
    # List files in working directory
    print("📁 Files in working directory:")
    for file in sorted(Path('.').iterdir()):
        if file.is_file():
            print(f"  - {file.name}")
    
    # Step 1: Install system dependencies
    print("\n🔧 Step 1: Installing system dependencies...")
    if not install_system_dependencies():
        print("❌ Failed to install system dependencies")
        sys.exit(1)
    
    # Step 2: Install Python dependencies
    print("\n🔧 Step 2: Installing Python requirements...")
    if not install_requirements():
        print("❌ Failed to install Python requirements")
        sys.exit(1)
    
    # Step 3: Set up environment
    print("\n🔧 Step 3: Setting up environment...")
    if not setup_environment():
        print("❌ Failed to setup environment")
        sys.exit(1)
    
    # Step 4: Run training
    print("\n🔧 Step 4: Running YOLO training...")
    if not run_yolo_training():
        print("❌ Training failed")
        sys.exit(1)
    
    print("🎉 All tasks completed successfully!")

if __name__ == "__main__":
    main() 