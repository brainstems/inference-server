#!/bin/bash

# Variables
REPO_LOCAL_PATH="/app/repo"

# Cambia al directorio de la aplicación
cd "$REPO_LOCAL_PATH"

# Ejecuta el servidor
echo "Running server"
python3 src/server.py