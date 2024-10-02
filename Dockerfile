# Start with a basic Ubuntu image
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gnupg2 \
    software-properties-common \
    curl \
    ca-certificates \
    lsb-release

# Add NVIDIA's CUDA GPG key and repository for CUDA 12.6
RUN curl -fsSL https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub | gpg --dearmor -o /usr/share/keyrings/cuda-keyring.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/cuda-keyring.gpg] https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/ /" | tee /etc/apt/sources.list.d/cuda.list

# Install CUDA 12.6
RUN apt-get update && apt-get install -y cuda-12-6

# Verify CUDA installation
RUN nvcc -V

# Install Python and pip
RUN apt-get install -y python3-pip

# Install llama-cpp-python with CUDA support
RUN CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 pip3 install llama-cpp-python

# Install PyTorch with CUDA support
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install mamba-ssm and causal-conv1d
RUN pip3 install mamba-ssm causal-conv1d>=1.2.0 --root-user-action=ignore

# Set the working directory
WORKDIR /app

# Copy the Python dependencies file and install
COPY requirements.txt /app/repo/
RUN pip3 install --default-timeout=100 -r /app/repo/requirements.txt --root-user-action=ignore

# Install additional dependencies like boto3 and pymongo
RUN pip3 install boto3 pymongo --root-user-action=ignore

# Copy the entrypoint script and give it execution permissions
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy project files
COPY src /app/repo/src
COPY model /app/repo/model

# Expose WebSocket and HTTP ports
EXPOSE 8000 8080

# Set environment variables for MongoDB and AWS
ARG REPO_URL
ARG REPO_BRANCH
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION
ARG MONGO_URI

ENV REPO_URL=${REPO_URL}
ENV REPO_BRANCH=${REPO_BRANCH}
ENV AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
ENV AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
ENV AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
ENV MONGO_URI=${MONGO_URI}

# Add the src folder to PYTHONPATH
ENV PYTHONPATH="/app/repo/src:${PYTHONPATH}"

# Set the entry point for the container
ENTRYPOINT ["python3", "/app/repo/src/server.py"]