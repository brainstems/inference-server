# Use the NVIDIA CUDA base image for ARM64 architecture (for M2 Mac)
FROM --platform=linux/amd64 nvidia/cuda:12.4.1-cudnn-devel-ubuntu20.04

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ./server.py /app/server.py
COPY ./dolphin-2.6-mistral-7b.Q8_0.gguf /app/dolphin-2.6-mistral-7b.Q8_0.gguf

# Install the needed packages
RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install llama-cpp-python
RUN pip3 install Flask

# Expose port 8000 outside of the container
EXPOSE 8000

# Run server.py when the container launches
CMD ["python3", "server.py"]