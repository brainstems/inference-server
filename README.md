# Inference Server
This server provides inferencing by hosting LLM.

## Dependencies
Tested on:
- Linux Debian 12 x64
- Python 3.11

Export env vars
```
export MODEL_REPO="TheBloke/dolphin-2.0-mistral-7B-GGUF"
export MODEL_FILE="dolphin-2.0-mistral-7b.Q4_K_M.gguf"

# These are required to have GPU acceleretaion.
export LLAMA_CPP_LIB=path/to/libllama.so
export LD_LIBRARY_PATH=.
```
The `libllama.so` and `libggml.so` files are the `llama-cpp-python` Linux x64 dynamic libraries compiled with GPU support. It is required to have GPU acceletation.

For further information refer to:
- https://github.com/abetlen/llama-cpp-python/issues/509
- https://github.com/ggerganov/llama.cpp


Create Python virtual environement
```
python3 -m venv v-env
source v-venv/bin/activate
```
Install dependencies
```
pip install -r requirements.txt
```

## Running
Enter the virtual environemnt created in the previous step
```
source v-venv/bin/activate
```
Run the Inference Server
```
python server.py
```

## Building Docker

Download the model and put it in a `model` directory at the project level.
```
mkdir -p model && \
wget -P model https://huggingface.co/TheBloke/dolphin-2.0-mistral-7B-GGUF/resolve/main/dolphin-2.0-mistral-7b.Q4_K_M.gguf
```

Building the docker image
```
docker build -t ernestbs/inference-server:v0.1.2-x64-cu12.4-ubu22 .
```

## Running Docker
```
docker run --name inference-server --gpus all \
    -p 8000:8000 \
    -e MODEL_REPO="TheBloke/dolphin-2.0-mistral-7B-GGUF" \
    -e MODEL_FILE="dolphin-2.0-mistral-7b.Q4_K_M.gguf" \
    -e REPO_URL="https://github.com/brainstems/inference-server.git" \
    -e REPO_BRANCH="main" \
    ernestbs/inference-server:v0.1.2-x64-cu12.4-ubu22
```
