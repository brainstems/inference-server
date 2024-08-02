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
mv libllama.so inference-server/
mv libggml.so inference-server/
mv libcudart.so.11.8.89 inference-server/

cd "$REPO_LOCAL_PATH"
echo "Generating links for dependencies"
ln -s libcudart.so.11.8.89 libcudart.so
ln -s libcudart.so.11.8.89 libcudart.so.11
ln -s libcudart.so.11.8.89 libcudart.so.11.0

# Set the path for the libraries that provide GPU acceleration.
echo "Exporting env vars"
echo "export LLAMA_CPP_LIB=libllama.so" >> ~/.bashrc
echo "export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:." >> ~/.bashrc
export LLAMA_CPP_LIB=libllama.so
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:.

# Run the application
echo "Running server"
python3 server.py
