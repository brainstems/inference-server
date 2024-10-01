# The NVIDIA CUDA base image with CUDNN support for Ubuntu 22.04 and CUDA 12.4.1
FROM --platform=linux/amd64 nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# Set the working directory in the container
WORKDIR /app

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    git \
    wget \
    python3-pip \
    cmake \
    nvidia-cuda-toolkit

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install llama-cpp-python with CUDA support
RUN CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 pip3 install llama-cpp-python

# Install PyTorch with CUDA 12.1 support (cu121)
RUN CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install mamba-ssm and causal-conv1d
RUN pip3 install mamba-ssm causal-conv1d>=1.2.0 --root-user-action=ignore

# Copy the Python dependencies file and install the requirements
COPY requirements.txt /app/repo/
RUN pip3 install --default-timeout=100 -r /app/repo/requirements.txt --root-user-action=ignore

# Install boto3 and pymongo for MongoDB and AWS credentials management
RUN pip3 install boto3 pymongo --root-user-action=ignore

# Copy the entrypoint script and give it execution permissions
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy project files (including model operations and other necessary files)
COPY src /app/repo/src
COPY model /app/repo/model

# Expose the WebSocket and HTTP ports
EXPOSE 8000 8080

# Environment variables for MongoDB and AWS credentials
ARG REPO_URL
ARG REPO_BRANCH
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION
ARG MONGO_URI

# Set environment variables
ENV REPO_URL=${REPO_URL}
ENV REPO_BRANCH=${REPO_BRANCH}
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
ENV MONGO_URI=${MONGO_URI}

# Add the src folder to the PYTHONPATH
ENV PYTHONPATH="/app/repo/src:${PYTHONPATH}"

# Set the entry point for the container to run the server
ENTRYPOINT ["python3", "/app/repo/src/server.py"]