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
    template = "<|im_start|>system\n{system_context}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n{assistant_context}<|im_end|>"
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
    try:
        tokens = model.tokenize(prompt.encode())  # 'prompt.encode()' converts the string to bytes."
    except Exception as e:
        reason = "Invalid prompt."
        print(reason)
        model.reset()
        yield reason
        return

    for token in model.generate(tokens):
        try:
            detokenized = model.detokenize([token])
            token_str = detokenized.decode("utf-8")
            if token_str == "" or token_str is None:
                return
            token_print = f'{{"token": "{token_str}"}}'
            print(token_print)
            yield token_print
        except Exception as e:
            print(f"Could not decode token: {e}")

async def keep_alive(websocket):
    while True:
        try:
            pong_waiter = await websocket.ping()
            await pong_waiter 
            print("Heart beat received")
            await asyncio.sleep(30) # Send a ping every 30 seconds
        except websockets.ConnectionClosed:
            break
        except Exception as e:
            print(f"Error in keep_alive: {e}")
            break

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
