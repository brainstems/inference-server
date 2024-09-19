# The NVIDIA CUDA base image. CUDA 12.5.0 images fail on Akash.
FROM --platform=linux/amd64 nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# Set the working directory in the container
WORKDIR /app

# Install necessary packages
RUN apt-get update && apt-get install -y \
    git \
    wget \
    python3-pip \
    nvidia-cuda-toolkit

# Install Python dependencies
RUN pip install --upgrade pip

# Install llama-cpp-python with CUDA support
RUN CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 pip3 install llama-cpp-python

# Install additional Python dependencies
COPY requirements.txt /app/repo/
RUN pip3 install --default-timeout=100 -r /app/repo/requirements.txt

# Add MongoDB and AWS credentials packages
RUN pip3 install boto3 pymongo

# Copy the entrypoint script into the container.
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy project files (including model operations and other necessary files)
COPY src /app/repo/src
COPY model /app/repo/model

# Expose the WebSocket and HTTP ports
EXPOSE 8000 8080

# Env vars for MongoDB and AWS credentials.
# You can set these dynamically during `docker run`.
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

# Set the entry point for the container.
ENTRYPOINT ["/app/entrypoint.sh"]