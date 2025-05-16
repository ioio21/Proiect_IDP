#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo -e "${YELLOW}Loading environment variables from .env file...${NC}"
    export $(cat .env | xargs)
else
    echo -e "${YELLOW}No .env file found, using default values...${NC}"
    export POSTGRES_USER=postgres
    export POSTGRES_PASSWORD=postgres
    export POSTGRES_DB=app
fi

# Set kubectl to skip TLS verification
export KUBECTL_OPTS="--insecure-skip-tls-verify"

echo -e "${YELLOW}Pulling images...${NC}"
docker pull ghcr.io/ioio21/auth-service:latest
docker pull ghcr.io/ioio21/product-service:latest
docker pull ghcr.io/ioio21/orders-service:latest

echo -e "${YELLOW}Starting deployment of microservices...${NC}"

# Function to apply manifests with status
apply_manifest() {
    echo -e "${YELLOW}Applying $1...${NC}"
    kubectl apply -f $1
    echo -e "${GREEN}Successfully applied $1${NC}"
}

# Create namespace first
apply_manifest "./k8s/namespace.yaml"

# Apply secrets
apply_manifest "./k8s/postgres-secret.yaml"

# Apply PostgreSQL
apply_manifest "./k8s/postgres.yaml"

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
kubectl $KUBECTL_OPTS wait --namespace microservices \
  --for=condition=ready pod \
  --selector=app=postgres \
  --timeout=120s

# Apply Kong configuration
apply_manifest "./k8s/kong-config.yaml"

# Apply Kong
apply_manifest "./k8s/kong.yaml"

# Wait for Kong to be ready
echo -e "${YELLOW}Waiting for Kong to be ready...${NC}"
kubectl $KUBECTL_OPTS wait --namespace microservices \
  --for=condition=ready pod \
  --selector=app=kong \
  --timeout=120s

# Apply microservices
apply_manifest "./k8s/microservices.yaml"

# Wait for all deployments to be ready
echo -e "${YELLOW}Waiting for all deployments to be ready...${NC}"
kubectl $KUBECTL_OPTS wait --namespace microservices \
  --for=condition=available \
  --timeout=300s \
  deployment/auth-service \
  deployment/product-service \
  deployment/orders-service

# Get Kong proxy service external IP
echo -e "${YELLOW}Getting Kong proxy service external IP...${NC}"
KONG_IP=$(kubectl $KUBECTL_OPTS get service -n microservices kong-proxy -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

if [ -z "$KONG_IP" ]; then
    echo -e "${YELLOW}Waiting for Kong LoadBalancer IP...${NC}"
    sleep 10
    KONG_IP=$(kubectl $KUBECTL_OPTS get service -n microservices kong-proxy -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
fi

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Kong proxy is available at: http://${KONG_IP}${NC}"
echo -e "${GREEN}Available endpoints:${NC}"
echo -e "  - Auth Service: http://${KONG_IP}/auth"
echo -e "  - Product Service: http://${KONG_IP}/products"
echo -e "  - Orders Service: http://${KONG_IP}/orders" 