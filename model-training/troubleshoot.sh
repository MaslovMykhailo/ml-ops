#!/bin/bash

echo "=== Ray Cluster Troubleshooting Script ==="
echo ""

echo "1. Checking cluster status..."
kubectl cluster-info

echo ""
echo "2. Checking node resources..."
kubectl top nodes 2>/dev/null || echo "Metrics server not available"

echo ""
echo "3. Checking all namespaces..."
kubectl get namespaces

echo ""
echo "4. Checking prometheus-system namespace..."
kubectl get all -n prometheus-system

echo ""
echo "5. Checking for failed pods..."
kubectl get pods --all-namespaces --field-selector=status.phase=Failed

echo ""
echo "6. Checking for pending pods..."
kubectl get pods --all-namespaces --field-selector=status.phase=Pending

echo ""
echo "7. Checking events in prometheus-system..."
kubectl get events -n prometheus-system --sort-by='.lastTimestamp'

echo ""
echo "8. Checking Helm releases..."
helm list -A

echo ""
echo "9. Checking storage classes..."
kubectl get storageclass

echo ""
echo "10. Checking persistent volumes..."
kubectl get pv

echo ""
echo "11. Checking persistent volume claims..."
kubectl get pvc -A

echo ""
echo "12. Checking if there are resource constraints..."
kubectl describe nodes | grep -A5 "Allocated resources"

echo ""
echo "=== Troubleshooting Complete ==="
echo ""
echo "If you see issues with:"
echo "- Storage: Check if local-path-storage is working"
echo "- Resources: Your system might need more CPU/memory"
echo "- Network: Check if all required images were loaded"
echo "- Timeouts: Increase timeout values or reduce resource requirements" 