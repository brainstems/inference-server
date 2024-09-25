import asyncio
import json
import logging
import sys

import websockets
from aiohttp import web
from dotenv import load_dotenv

from app import add_model_handler, activate_model_handler, delete_model_handler, list_models_handler, model_service
from models.models import ModelSchema
from services.engine_models import EngineService
from cuda_utils import cuda_is_available
load_dotenv()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


async def handler(websocket, path):
    """
    Handles incoming WebSocket connections, receives prompts, and generates tokens.
    """
    try:
        prompt = await websocket.recv()
        tag = json.loads(prompt)['tag']
        logging.info(f'Current Tag: {tag}')
        # model_metadata = model_service.get_active_model(tag=tag)
        # logging.info(f'Model Validation Exists process')
        # if not model_metadata:
        #     logging.info(f'Model Validation Exists')
        #     raise Exception("No active model found in the database.")

        model_metadata = ModelSchema(
            **{
                "enabled": True,
                "engine": "transformer",
                "last_updated": "2024-09-09T00:00:00Z",
                # "model_name": "models--ai21labs--AI21-Jamba-1.5-Mini/snapshots/1840d3373c51e4937f4dbaaaaf8cac1427b46858",
                "model_name": "models--ai21labs--AI21-Jamba-1.5-Mini/snapshots/83cec42f3448800e888c69f892e65ec8c73de225",
                # "s3_path": "s3://is-models/snapshots/1840d3373c51e4937f4dbaaaaf8cac1427b46858/",
                "s3_path": "s3://is-models/snapshots/83cec42f3448800e888c69f892e65ec8c73de225/",
                "tag": "jamba"
            }
        )
        logging.info(f'Checking process step')
        model_path = model_service.ensure_model_exists(model_metadata.model_name, model_metadata.s3_path,
                                                       model_metadata.engine)
        logging.info(f"Loading model from {model_path}")

        service = EngineService(model_metadata.engine, model_metadata)
        response = service.process(prompt)
        websocket.send(response)

    except websockets.ConnectionClosedError:
        logging.info("Connection closed unexpectedly. Cleaning up...")
    except websockets.ConnectionClosedOK:
        logging.info("Connection closed normally.")
    except Exception as e:
        logging.info(f"Connection error: {e}")


async def handle_health_check(request):
    """
    Health check endpoint.
    """
    return web.Response(text="OK")


async def start_websocket_server():
    """
    Starts the WebSocket server on port 8000.
    """
    logging.info(f"Cuda device enabled {cuda_is_available()}")
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
