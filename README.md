# Inference Server
This server provides inferencing by hosting LLM.

## Building
```
docker build -t ernestbs/jedai-akash-poc:v0.1.0-cu12.4-ubu22 .
```

## Running
```
docker run --name inference-server --gpus all \
    -p 8000:8000 \
    -e MODEL_REPO="TheBloke/dolphin-2.6-mistral-7B-dpo-laser-GGUF" \
    -e MODEL_FILE="dolphin-2.0-mistral-7b.Q5_K_S.gguf" \
    -e REPO_URL="https://github.com/brainstems/brainstems-jedai-akash-poc.git" \
    -e REPO_BRANCH="feat/TheBloke_dolphin-2.0-mistral-7B-GGUF" \
    ernestbs/jedai-akash-poc:v0.1.0-cu12.4-ubu22
```
