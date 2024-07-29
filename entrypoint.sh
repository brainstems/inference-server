#!/bin/bash

# Variables
#REPO_URL="https://github.com/brainstems/brainstems-jedai-akash-poc.git"
REPO_LOCAL_PATH="/app/repo/brainstems-jedai-akash-poc"
APP_DIR="/app/repo"
#REPO_BRANCH=feat/websockets-server
#MODEL_URL="TheBloke/Llama-2-7B-Chat-GGUF"
#MODEL_PATH="llama-2-7b-chat.Q5_K_S.gguf"

# Change to the app directory
cd $APP_DIR

# Clone the repository
echo "Cloning repository branch $REPO_BRANCH"
git clone -b "$REPO_BRANCH" "$REPO_URL"

cd "$REPO_LOCAL_PATH"

# Export the model path environment variable
#export MODEL_PATH="$MODEL_PATH"

# Run the application
python3 server.py
