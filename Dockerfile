# The NVIDIA CUDA base image. CUDA 12.5.0 images fail on Akash.
FROM --platform=linux/amd64 nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# Set the working directory in the container
WORKDIR /app

# Install necessary packages
RUN apt-get update && apt-get install -y git wget libcublas11 python3-pip python3-venv

# Copy the entrypoint script into the container.
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy files and dirs.
COPY requirements.txt /app/repo/
COPY model /app/repo/model
COPY libllama.so /app/repo/
COPY libggml.so /app/repo/
COPY libcudart.so.11.8.89 /app/repo/

# Install project dependencies.
RUN pip3 install --default-timeout=100 -r /app/repo/requirements.txt

EXPOSE 8000

# Env vars.
ARG MODEL_REPO
ARG MODEL_FILE
ARG REPO_URL
ARG REPO_BRANCH

ENV MODEL_URL={MODEL_REPO}
ENV MODEL_FILE={MODEL_FILE}
ENV REPO_URL={REPO_URL}
ENV REPO_BRANCH={REPO_BRANCH}

ENTRYPOINT ["/app/entrypoint.sh"]
