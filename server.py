import os
import asyncio
import json
import websockets
import torch
from transformers import AutoTokenizer
from llama_cpp import Llama

# Ensure the model is loaded on the GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"device set to: {device}")

# Load the model and tokenizer
model_name = os.environ['MODEL_REPO']
model_file = os.environ['MODEL_FILE']
model_path = f"model/{model_file}"
print("Loading model")
model = Llama(model_path=model_path, use_gpu=True, n_gpu_layers=50)
print("Loading tokenizer")
tokenizer = AutoTokenizer.from_pretrained(model_name, gguf_file=model_file)
print("Server ready")

async def generate_tokens(prompt):
    template = "system\n{system_context}\nuser\n{user_prompt}\nassistant\n{assistant_context}"
    try:
        json_prompt = json.loads(prompt)
        if 'system_context' in json_prompt and 'user_prompt' in json_prompt and 'max_tokens' in json_prompt and 'assistant_context' in json_prompt:
            system_context = json_prompt['system_context']
            user_prompt = json_prompt['user_prompt']
            max_tokens = int(json_prompt['max_tokens'])
            assistant_context = json_prompt['assistant_context']
            # Create the prompt using the template
            prompt = template.format(system_context=system_context, user_prompt=user_prompt, assistant_context=assistant_context)
        else:
            reason = "Prompt missing field(s)."
            print(reason)
            yield reason
            return
    except:
        reason = "Bad prompt."
        print(reason)
        yield reason
        return
    
    print("Encoding tokens.")
    tokens = model.tokenize(prompt.encode())  # 'prompt.encode()' converts the string to bytes."
    for token in model.generate(tokens):
        detokenized = model.detokenize([token])
        token_str = detokenized.decode("utf-8")
        if token_str == "" or token_str is None:
            eor = "END_OF_RESPONSE"
            print(eor)
            yield eor
            break
        token_print = f'{{"token": "{token_str}"}}'
        print(token_print)
        yield token_print

async def keep_alive(websocket):
    while True:
        try:
            pong_waiter = await websocket.ping()
            await pong_waiter 
            print("Heart beat received")
            await asyncio.sleep(30) # Send a ping every 30 seconds
        except websockets.ConnectionClosed:
            break

async def handler(websocket, path):
    prompt = await websocket.recv()
    async for token in generate_tokens(prompt):
        await websocket.send(token)
    #keep_alive_task = asyncio.create_task(keep_alive(websocket))
    #try:
        #pong_waiter = await websocket.ping()
        #await pong_waiter
    #    async for message in websocket:
    #        await generate_tokens(message, websocket)
    #except websockets.ConnectionClosedError:
    #    print("Connection closed unexpectedly. Cleaning up...")
    #except websockets.ConnectionClosedOK:
    #    print("Connection closed normally.")
    #finally:
    #    keep_alive_task.cancel()
    #    await keep_alive_task

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
