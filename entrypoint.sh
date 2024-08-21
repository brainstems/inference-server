#!/bin/bash

# Variables
REPO_LOCAL_PATH="/app/repo/inference-server"

# Change to the app directory
cd "/app/repo"

# Clone the repository
echo "Cloning repository branch $REPO_BRANCH"
git clone -b "$REPO_BRANCH" "$REPO_URL"

# Move the model dir to the inference-server dir.
echo "Moving files to repo dir"
mv model/ inference-server/

cd "$REPO_LOCAL_PATH"

# Run the application
echo "Running server"
python3 src/server.py
