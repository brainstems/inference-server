#!/bin/bash

# Variables
REPO_LOCAL_PATH="/app/repo/brainstems-jedai-akash-poc"

# Change to the app directory
cd "/app/repo"

# Clone the repository
echo "Cloning repository branch $REPO_BRANCH"
git clone -b "$REPO_BRANCH" "$REPO_URL"

cd "$REPO_LOCAL_PATH"

# Run the application
python3 server.py
