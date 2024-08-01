#!/bin/bash

# Variables
REPO_LOCAL_PATH="/app/repo/inference-server"

# Change to the app directory
cd "/app/repo"

# Clone the repository
echo "Cloning repository branch $REPO_BRANCH"
git clone -b "$REPO_BRANCH" "$REPO_URL"

# Move the model dir to the inference-server dir.
mv model/ inference-server/
mv libllama.so inference-server/

cd "$REPO_LOCAL_PATH"

# Run the application
python3 server.py
