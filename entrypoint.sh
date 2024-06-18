#!/bin/bash

# Variables
REPO_URL="https://github.com/brainstems/brainstems-jedai-akash-poc.git"
REPO_DIR="/app/repo"
MODEL_URL=${MODEL_URL:-"TheBloke/Llama-2-7B-Chat-GGUF"}
MODEL_PATH=${MODEL_PATH:-"llama-2-7b-chat.Q5_K_S.gguf"}

# Clone the repository
if [ -d "$REPO_DIR" ]; then
    echo "Repository already exists, pulling the latest changes..."
    cd $REPO_DIR && git pull
else
    echo "Cloning repository..."
    git clone $REPO_URL $REPO_DIR
fi

# Download the model file
if [ ! -f "$MODEL_PATH" ]; then
    echo "Downloading the model file..."
    python3 /app/repo/download_model.py "$MODEL_URL" "$MODEL_PATH"
fi

# Export the model path environment variable
export MODEL_PATH=$MODEL_PATH

# Change to the repository directory
cd $REPO_DIR

# Run the application
python3 server.py