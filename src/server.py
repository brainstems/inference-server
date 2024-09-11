import asyncio
import os

import boto3
import websockets
from aiohttp import web
from dotenv import load_dotenv

from app import add_model_handler, activate_model_handler, delete_model_handler, list_models_handler, model_service
from model_operations import generate_tokens, load_model

load_dotenv()


def download_model_from_s3(s3_path, local_path):
    """
    Downloads the model from S3 if it's not already present locally.
    """
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name="us-east-1"
    )
    bucket, key = s3_path.replace("s3://", "").split("/", 1)
    s3.download_file(bucket, key, local_path)


def ensure_model_exists(model_name, model_s3_path):
    """
    Ensures the model exists locally, downloading it from S3 if necessary.
    """
    local_model_path = f"../model/{model_name}.gguf"
    if not os.path.exists(local_model_path):
        print(f"Downloading model from {model_s3_path}")
        download_model_from_s3(model_s3_path, local_model_path)
    return local_model_path


async def handler(websocket, path):
    """
    Handles incoming WebSocket connections, receives prompts, and generates tokens.
    """
    try:
        prompt = await websocket.recv()

        model_metadata = model_service.get_active_model()
        if not model_metadata:
            raise Exception("No active model found in the database.")

        model_path = ensure_model_exists(model_metadata.model_name, model_metadata.s3_path)
        print(f"Loading model from {model_path}")
        model = load_model(model_path=model_path, n_ctx=4096)
        print("Model loaded successfully.")

        async for token in generate_tokens(prompt, model):
            await websocket.send(token)

    except websockets.ConnectionClosedError:
        print("Connection closed unexpectedly. Cleaning up...")
    except websockets.ConnectionClosedOK:
        print("Connection closed normally.")
    except Exception as e:
        print(f"Connection error: {e}")


async def handle_health_check(request):
    """
    Health check endpoint.
    """
    return web.Response(text="OK")


async def start_websocket_server():
    """
    Starts the WebSocket server on port 8000.
    """
    try:
        async with websockets.serve(handler, "0.0.0.0", 8000):
            print("WebSocket server running on ws://0.0.0.0:8000")
            await asyncio.Future()  # run forever
    except Exception as e:
        print(f"Error starting WebSocket server: {e}")


async def start_http_server():
    """
    Starts the HTTP server with endpoints for model management.
    """
    app = web.Application()

    # API Routes
    app.router.add_post('/models', add_model_handler)
    app.router.add_put('/models/{model_id}/activate', activate_model_handler)
    app.router.add_delete('/models/{model_id}', delete_model_handler)
    app.router.add_get('/models', list_models_handler)

    # Health check
    app.router.add_get('/health', handle_health_check)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("HTTP server running on http://0.0.0.0:8080")


async def main():
    """
    Starts both WebSocket and HTTP servers concurrently.
    """
    await asyncio.gather(
        start_websocket_server(),
        start_http_server(),
    )


if __name__ == "__main__":
    asyncio.run(main())
