import asyncio
import json

import websockets
from aiohttp import web
from dotenv import load_dotenv

from app import add_model_handler, activate_model_handler, delete_model_handler, list_models_handler, model_service
from src.services.engine_models import EngineService

load_dotenv()


async def handler(websocket, path):
    """
    Handles incoming WebSocket connections, receives prompts, and generates tokens.
    """
    try:
        prompt = await websocket.recv()
        tag = json.loads(prompt)['tag']
        model_metadata = model_service.get_active_model(tag=tag)
        if not model_metadata:
            raise Exception("No active model found in the database.")

        model_path = model_service.ensure_model_exists(model_metadata.model_name, model_metadata.s3_path,
                                                       model_metadata.engine)
        print(f"Loading model from {model_path}")

        service = EngineService(model_metadata.engine, model_metadata)
        response = service.process(prompt)
        websocket.send(response)

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
