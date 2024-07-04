#!/bin/bash

# Variables
REPO_URL="https://github.com/brainstems/brainstems-jedai-akash-poc.git"
REPO_BRANCH=test/newer-cuda-image
APP_DIR="/app/repo"
REPO_PATH="/app/repo/brainstems-jedai-akash-poc"
MODEL_URL="TheBloke/Llama-2-7B-Chat-GGUF"
MODEL_PATH="llama-2-7b-chat.Q5_K_S.gguf"

# Change to the app directory
cd $APP_DIR

Clone the repository
echo "Cloning repository branch $REPO_BRANCH"
git clone -b "$REPO_BRANCH" "$REPO_URL"

cd "$REPO_PATH"

# Download the model file
if [ ! -f "$MODEL_PATH" ]; then
    echo "Downloading the model file..."
    python3 download_model.py "$MODEL_URL" "$MODEL_PATH"
fi

# Export the model path environment variable
export MODEL_PATH="$MODEL_PATH"

# Run the application
python3 server.py
