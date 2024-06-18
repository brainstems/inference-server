# Use the NVIDIA CUDA base image for ARM64 architecture (for M2 Mac)
FROM --platform=linux/amd64 nvidia/cuda:12.4.1-cudnn-devel-ubuntu20.04

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

# Copy the requirements file and install Python packages
COPY requirements.txt /app/requirements.txt
RUN python3 -m pip install --upgrade pip && \
    pip3 install --default-timeout=100 -r /app/requirements.txt

# Clean up APT when done
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Expose port 8000 outside of the container
EXPOSE 8000

# Run the entrypoint script when the container starts
ENTRYPOINT ["/app/entrypoint.sh"]