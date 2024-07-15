import asyncio
import json
import websockets
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Ensure the model is loaded on the GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"device set to: {device}")

# Load the model and tokenizer
print("Loading model... ")
model_name = "cognitivecomputations/dolphin-2.0-mistral-7b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
print("Server ready")

async def generate_tokens(prompt, websocket):
    await websocket.send("Generating tokens")
    template = "system\n{system_context}\nuser\n{user_prompt}\nassistant\n{assistant_context}"
    json_prompt = json.loads(prompt)
    if 'system_context' in json_prompt and 'user_prompt' in json_prompt and 'max_tokens' in json_prompt and 'assistant_context' in json_prompt:
        system_context = json_prompt['system_context']
        user_prompt = json_prompt['user_prompt']
        max_tokens = int(json_prompt['max_tokens'])
        assistant_context = json_prompt['assistant_context']
        # Create the prompt using the template
        prompt = template.format(system_context=system_context, user_prompt=user_prompt, assistant_context=assistant_context)
        print(f"system_context: {system_context}")
        print(f"user_prompt: {user_prompt}")
        print(f"assistant_context: {assistant_context}")
        print(f"prompt: {prompt}")

    input_ids = tokenizer.encode(prompt, return_tensors='pt')
    output_ids = input_ids

    print("Generate token-by-token")
    await websocket.send("Sending token-by-token")
    # Generate token-by-token
    for _ in range(max_tokens):
        outputs = model(output_ids)
        next_token_logits = outputs.logits[:, -1, :]
        next_token_id = torch.argmax(next_token_logits, dim=-1)
        output_ids = torch.cat([output_ids, next_token_id.unsqueeze(-1)], dim=-1)
        next_token = tokenizer.decode(next_token_id)
        print(f"next_token: {next_token}")
        await websocket.send(next_token)
        if next_token in tokenizer.eos_token:
            break

async def test1(prompt, websocket):
    print(f"test1 called!")
    await websocket.send("Hello")


async def handler(websocket, path):
    async for message in websocket:
        await generate_tokens(message, websocket)
        #await test1(message, websocket)

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
