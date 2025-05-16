#!/bin/bash

# Script pentru pornirea monitorizării cu Prometheus și Grafana
# Autor: Echipa IDP

set -e

echo "=== Verificarea dependențelor Python ==="
if ! grep -q "prometheus-client" backend/requirements.txt; then
    echo "Adăugare prometheus-client la requirements.txt"
    echo "prometheus-client>=0.16.0" >> backend/requirements.txt
fi

echo "=== Instalarea dependențelor Python ==="
cd backend
python -m pip install -r requirements.txt
cd ..

echo "=== Reconstruirea containerelor cu Docker Compose ==="
docker-compose build

echo "=== Pornirea serviciilor ==="
docker-compose up -d

echo "=== Configurare completă ==="
echo "Poți accesa:"
echo "- Kong API Gateway: http://localhost:8000"
echo "- Kong Admin API: http://localhost:8001"
echo "- Konga (Kong UI): http://localhost:1337"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3000 (admin/admin)"
echo "- cAdvisor: http://localhost:8080"