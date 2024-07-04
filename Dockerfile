# The NVIDIA CUDA base image. CUDA 12.5.0 images fail on Akash.
FROM --platform=linux/amd64 nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# Set the working directory in the container
WORKDIR /app

# Install necessary packages
RUN apt-get update && apt-get install -y \
    python3-pip \
    git \
    wget

# Copy the entrypoint script into the container
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy files.
# COPY requirements.txt entrypoint.sh server.py \
#     app.py akash_gpu.sdl download_model.py /app/repo/
COPY requirements.txt /app/repo/

# Install project dependencies.
RUN python3 -m pip install --upgrade pip && \
    pip3 install --default-timeout=100 -r /app/repo/requirements.txt > /app/pip-install-output

# Clean up APT when done
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
