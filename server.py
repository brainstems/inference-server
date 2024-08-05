import os
import asyncio
import json
import websockets
import torch
from llama_cpp import Llama

# Ensure the model is loaded on the GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"device set to: {device}")

# Load the model and tokenizer
preemptiveness = os.getenv("PREEMPTIVENESS", "0")
print(f"Preemptiveness: {preemptiveness}")
model_name = os.environ['MODEL_REPO']
model_file = os.environ['MODEL_FILE']
model_path = f"model/{model_file}"
print(f"Loading model: {model_file}")
model = Llama(model_path=model_path, use_gpu=True, n_gpu_layers=-1,
              n_ctx = 4096,
              n_threads = 4,
              stop=[""])
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
            # EXPERIMENTAL:
            #   Due to lack of scheduling once entered this 'for generation loop', we simulte preemptiveness to have parallelism.
            #   We did not have good stable results so far. Be aware that this implementation introduces latency per token generation.
            if preemptiveness == "1":
                await asyncio.sleep(0.01)
            detokenized = model.detokenize([token])
            token_str = detokenized.decode("utf-8")
            # 'stop' setting param does not seem to be working when loading the model. So, we stop when start receiving empty responses.
            if token_str == "" or token_str is None:
                return
            token_print = f'{{"token": "{token_str}"}}'
            print(token_print)
            yield token_print
        except Exception as e:
            print(f"Could not decode token: {e}")

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
