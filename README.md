# Inference Server
This server provides inferencing by hosting LLM.

## Dependencies
Tested on:
- Linux Debian 12 x64
- Python 3.11
- Pytest, Pytest-asyncio (Optional, if you want to run unit tests)

Create Python virtual environement
```
python3 -m venv v-env
source v-venv/bin/activate
```
Install dependencies
```
CMAKE_ARGS="-DGGML_CUDA=on" FORCE_CMAKE=1 pip3 install llama-cpp-python
pip install -r requirements.txt
```
`llama-cpp-python` needs to be installed with CUDA support, as performed in the command above.

## Running
Enter the virtual environemnt created in the previous step
```
source v-venv/bin/activate
```
Run the Inference Server
```
python server.py
```

## Running unit tests
Pytest is required. Also `pytest-asyncio` to test `async` functions.
```
pip install pytest pytest-asyncio
```
Setup the ENV environment variable to `TESTING`
```
export ENV=TESTING
```
Run the tests
```
pytest [test/<unit_tests>]
```
For instance
```
pytest
```

## Building Docker

Download the model and put it in a `model` directory at the project level.
```
mkdir -p model && \
wget -P model https://huggingface.co/TheBloke/dolphin-2.0-mistral-7B-GGUF/resolve/main/dolphin-2.0-mistral-7b.Q4_K_M.gguf
```

Building the docker image
```
docker build -t ernestbs/inference-server:v0.4.0-cu124-ubu22 .
```

## Running Docker
```
docker run --name inference-server --gpus all \
    -p 8000:8000 -p 8080:8080 \
    -e AWS_ACCESS_KEY_ID="your-access-key-id" \
    -e AWS_SECRET_ACCESS_KEY="your-secret-access-key" \
    -e AWS_DEFAULT_REGION="us-west-2" \
    -e MONGO_URI="mongodb://localhost:27017" \
    inference-server-custom:latest
```
