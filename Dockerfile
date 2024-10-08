# Start with the NVIDIA CUDA base image with CUDNN support for Ubuntu 22.04 and CUDA 12.4.1
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

# Download and configure the CUDA repository for Ubuntu 20.04 (required for CUDA 12.4)
RUN wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin \
    && mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600 \
    && wget https://developer.download.nvidia.com/compute/cuda/12.4.0/local_installers/cuda-repo-ubuntu2004-12-4-local_12.4.0-550.54.14-1_amd64.deb \
    && dpkg -i cuda-repo-ubuntu2004-12-4-local_12.4.0-550.54.14-1_amd64.deb \
    && cp /var/cuda-repo-ubuntu2004-12-4-local/cuda-*-keyring.gpg /usr/share/keyrings/ \
    && apt-get update && apt-get install -y cuda-toolkit-12-4

# Set CUDA environment variables explicitly
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=$CUDA_HOME/bin:$PATH
ENV LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install Hugging Face Transformers library
RUN pip install transformers

# Install PyTorch with CUDA 12.1 support (cu121)
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install mamba-ssm and causal-conv1d with CUDA support
RUN pip3 install mamba-ssm 'causal-conv1d>=1.2.0' --root-user-action=ignore

# Set the Hugging Face Token as an ARG and add it directly to the Hugging Face config
ARG HF_TOKEN
RUN mkdir -p ~/.huggingface && \
    echo "{ \"token\": \"${HF_TOKEN}\" }" > ~/.huggingface/token

# Install Python dependencies from requirements.txt
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

# Expose WebSocket and HTTP ports
EXPOSE 8000 8080

# Environment variables for MongoDB and AWS credentials
ARG REPO_URL
ARG REPO_BRANCH
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION
ARG MONGO_URI

# Hugging Face environment variables
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