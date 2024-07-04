#docker run -d --name jedai-akash-poc ernestbs/jedai-akash-poc:v0.1
#docker run -p 8000:8000 --name jedai-akash-poc-d --gpus all ernestbs/jedai-akash-poc:v0.0.20-cu12.4-ubu22
docker run -p 8000:8000 --name jedai-akash-poc-d ernestbs/jedai-akash-poc:v0.0.20-cu12.4-ubu22
docker run --rm -p 8000:8000 --name jedai-akash-poc-d -it --entrypoint /bin/bash ernestbs/jedai-akash-poc:v0.0.22-cu12.4-ubu22
