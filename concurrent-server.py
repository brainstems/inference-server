import asyncio

import websockets

print("Server ready")


async def generate_tokens(prompt):
    for n in range(30):
        result = str(n)
        print(result)
        await asyncio.sleep(1)
        yield result


async def handler(websocket, path):
    try:
        prompt = await websocket.recv()
        async for token in generate_tokens(prompt):
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
