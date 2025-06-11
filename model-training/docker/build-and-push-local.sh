#!/bin/bash

IMAGE_NAME="ray-worker"
IMAGE_TAG="latest"
REGISTRY="localhost:5000"

FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "🔨 Building custom Ray image with OpenCV dependencies..."
echo "Image: ${FULL_IMAGE_NAME}"

docker build -t ${FULL_IMAGE_NAME} .

if [ $? -eq 0 ]; then
    echo "✅ Image built successfully!"

    echo "📝 Starting local Docker registry..."
    docker run -d -p 5000:5000 --name registry registry:2
    
    echo "🚀 Pushing image to registry..."
    docker push ${FULL_IMAGE_NAME}
    
    if [ $? -eq 0 ]; then
        echo "✅ Image pushed successfully!"
        echo "📝 Update your ray-cluster-values.yaml with:"
        echo "image:"
        echo "  repository: ${REGISTRY}/${IMAGE_NAME}"
        echo "  tag: \"${IMAGE_TAG}\""
    else
        echo "❌ Failed to push image"
        exit 1
    fi
else
    echo "❌ Failed to build image"
    exit 1
fi 