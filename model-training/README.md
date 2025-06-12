# ML Ops Model Training Project

This project implements a distributed model training solution using Ray cluster for YOLOv8 model training with Weights & Biases (W&B) integration for experiment tracking and model storage.

## Solution Overview

The implemented solution consists of several key components:

1. **Ray Cluster**: A distributed computing framework for scalable model training
2. **YOLOv8 Training**: Implementation of YOLOv8 model training on CPU
3. **Weights & Biases Integration**: For experiment tracking and model storage
4. **Kubernetes Deployment**: Containerized deployment using Kind cluster

## Setup Instructions

### 1. Set up Kubernetes Cluster

```bash
# Navigate to the project directory
cd model-training

# Run the setup script
sh ./setup_cluster.sh
```

This script will:

- Create a Kind cluster
- Deploy the Ray operator
- Set up the Ray cluster
- Configure necessary resources

### 2. Configure Weights & Biases

1. Create a W&B account at https://wandb.ai
2. Get your API key from your W&B account settings
3. Set the API key as an environment variable:

```bash
export WANDB_API_KEY='your-api-key'
```

## Running Model Training

### 1. Submit Training Job to Ray Cluster

```bash
cd ./model-training/model-cpu
RAY_ADDRESS='http://127.0.0.1:8265' ray job submit --working-dir . -- python submit_job.py
```

This will:

- Package training code
- Submit it to the Ray cluster
- Monitor the training progress

### 2. Monitor Training

- Check Ray dashboard for job status
- View training progress in W&B dashboard
- Monitor cluster resources using Kubernetes dashboard

## Using Weights & Biases

### Model Storage

The training script automatically saves models to W&B which allows to:

1. Access models through the W&B UI
2. Download models using the W&B API
3. Compare different training runs
4. Track metrics and hyperparameters

## Project Structure

```
model-training/
├── docker/           # Docker configuration files
├── kind/            # Kind cluster configuration
├── k8s/             # Kubernetes manifests
├── model-cpu/       # Training code
│   ├── train_yolo.py    # Main training script
│   ├── ray_job.py       # Ray job configuration
│   ├── submit_job.py    # Job submission script
│   └── config.yaml      # Training configuration
├── monitoring/      # Monitoring tools
└── ray-cluster/    # Ray cluster configuration
```

## Troubleshooting

If you encounter issues:

1. Check the troubleshooting script:
```bash
./troubleshoot.sh
```

2. Verify Ray cluster status:
```bash
kubectl get pods -n ray-system
```
