import asyncio

import websockets
from aiohttp import web

from cuda_utils import cuda_device_enable
from model_operations import generate_tokens, load_model

# Ensure the model is loaded on the GPU
print(f"device set to: {cuda_device_enable()}")

# Load the model and tokenizer
model_name = os.environ['MODEL_REPO']
model_file = os.environ['MODEL_FILE']
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


async def start_websocket_server():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        await asyncio.Future()  # run forever


async def handle_health_check(request):
    return web.Response(text="OK")


async def start_http_server():
    app = web.Application()
    app.add_routes([web.get('/health', handle_health_check)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("HTTP health check server running on http://0.0.0.0:8080/health")


async def main():
    await asyncio.gather(
        start_websocket_server(),
        start_http_server(),
    )


if __name__ == "__main__":
    asyncio.run(main())
