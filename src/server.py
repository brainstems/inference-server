import asyncio

import websockets

from cuda_utils import cuda_device_enable
from model_operations import generate_tokens, load_model

# Ensure the model is loaded on the GPU
print(f"device set to: {cuda_device_enable()}")

# Load the model and tokenizer
model_name = "TheBloke/dolphin-2.0-mistral-7B-GGUF"
model_file = "dolphin-2.0-mistral-7b.Q4_K_M.gguf"
model_path = f"model/{model_file}"
print("Loading model")
model = load_model(model_path=model_path, n_ctx=4096)
print("Server ready")


async def handler(websocket, path):
    try:
        prompt = await websocket.recv()
        async for token in generate_tokens(prompt, model):
            await websocket.send(token)
    except websockets.ConnectionClosedError:
        print("Connection closed unexpectedly. Cleaning up...")
    except websockets.ConnectionClosedOK:
        print("Connection closed normally.")
    except Exception as e:
        print(f"Connection error: {e}")


async def main():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
