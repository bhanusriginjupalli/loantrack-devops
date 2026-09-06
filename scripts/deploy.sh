#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="loantrack"
BACKEND_IMAGE="loantrack-backend:v1"
FRONTEND_IMAGE="loantrack-frontend:v1"

echo "==> Checking Minikube..."
minikube status

echo "==> Building backend image..."
docker build -t "${BACKEND_IMAGE}" ./backend

echo "==> Building frontend image..."
docker build -t "${FRONTEND_IMAGE}" ./frontend

echo "==> Loading images into Minikube..."
minikube image load "${BACKEND_IMAGE}"
minikube image load "${FRONTEND_IMAGE}"

echo "==> Creating namespace..."
kubectl apply -f k8s/namespace.yaml

echo "==> Applying configuration..."
kubectl apply -f k8s/config.yaml
kubectl apply -f k8s/db-init-configmap.yaml

echo "==> Ensuring application secret exists..."
if ! kubectl get secret loantrack-secret -n "${NAMESPACE}" >/dev/null 2>&1; then
    echo "ERROR: loantrack-secret does not exist."
    echo "Create it with:"
    echo "kubectl create secret generic loantrack-secret -n ${NAMESPACE} --from-literal=POSTGRES_PASSWORD=<password>"
    exit 1
fi

echo "==> Deploying PostgreSQL..."
kubectl apply -f k8s/postgres.yaml

echo "==> Waiting for PostgreSQL..."
kubectl wait --for=condition=ready pod/postgres-0 \
    -n "${NAMESPACE}" \
    --timeout=180s

echo "==> Deploying backend..."
kubectl apply -f k8s/backend.yaml

echo "==> Waiting for backend..."
kubectl rollout status deployment/backend -n "${NAMESPACE}" --timeout=180s

echo "==> Deploying frontend..."
kubectl apply -f k8s/frontend.yaml

echo "==> Waiting for frontend..."
kubectl rollout status deployment/frontend -n "${NAMESPACE}" --timeout=180s

echo
echo "==> LoanTrack deployment complete."
echo
echo "Application URL:"
minikube service frontend -n "${NAMESPACE}" --url