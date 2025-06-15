import ray
from ray import serve
import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

# Initialize Ray with task-level runtime environment
ray.init(
    address="ray://localhost:10001",
    runtime_env={
        "working_dir": ".",
        "pip": [
            "ultralytics",
            "wandb", 
            "python-dotenv",
            "opencv-python-headless",
            "matplotlib",
            "seaborn",
            "scikit-learn",
            "torch",
            "torchvision"
        ],
        "env_vars": {
            "OPENCV_IO_ENABLE_OPENEXR": "0",
            "OPENCV_IO_ENABLE_JASPER": "0", 
            "QT_QPA_PLATFORM": "offscreen",
            "MPLBACKEND": "Agg",
            # Pass wandb environment variables to Ray
            "WANDB_PROJECT": os.getenv("WANDB_PROJECT", "ml-ops-yolo-cpu"),
            "WANDB_ENTITY": os.getenv("WANDB_ENTITY", "maslov-mykhailo-set-university"),
            "WANDB_MODEL_ARTIFACT": os.getenv("WANDB_MODEL_ARTIFACT", "maslov-mykhailo-set-university-org/wandb-registry-model/TestCollection:v1"),
            "WANDB_API_KEY": os.getenv("WANDB_API_KEY", ""),
            "WANDB_MODE": os.getenv("WANDB_MODE", "online"),
            "WANDB_SILENT": "true"
        }
    }
)

# Import application after Ray initialization
from object_detection import entrypoint

# Start serve application
serve.run(entrypoint, name="yolo") 