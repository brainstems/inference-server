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
mv libggml.so inference-server/

cd "$REPO_LOCAL_PATH"

# Set the path for the libraries that provide GPU acceleration.
export LLAMA_CPP_LIB=libllama.so
export LD_LIBRARY_PATH=.

# Run the application
python3 server.py
