#!/bin/bash

# Variables
REPO_URL="https://github.com/brainstems/brainstems-jedai-akash-poc.git"
REPO_DIR="/app/repo"
MODEL_URL=${MODEL_URL:-"https://huggingface.co/TheBloke/dolphin-2.6-mistral-7B-dpo-laser-GGUF/resolve/main/dolphin-2.0-mistral-7b.Q5_K_S.gguf"}
MODEL_PATH="/app/repo/dolphin-2.0-mistral-7b.Q5_K_S.gguf"

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
    wget -O $MODEL_PATH $MODEL_URL
fi

# Change to the repository directory
cd $REPO_DIR

# Run the application
python3 server.py