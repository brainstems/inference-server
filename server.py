import asyncio
import json
import websockets
import torch
from llama_cpp import Llama

# Ensure the model is loaded on the GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"device set to: {device}")

# Load the model and tokenizer
#model_name = os.environ['MODEL_REPO']
model_name = "TheBloke/dolphin-2.0-mistral-7B-GGUF"
#model_file = os.environ['MODEL_FILE']
model_file = "dolphin-2.0-mistral-7b.Q4_K_M.gguf"
model_path = f"model/{model_file}"
print("Loading model")
model = Llama(model_path=model_path, use_gpu=True, n_gpu_layers=50)
print("Server ready")
#system_context = "You are ChatGPT, an advanced AI language model developed by OpenAI, based on the GPT-4 architecture. Your primary function is to assist users by providing accurate and contextually relevant information, generating creative content, and offering guidance across a wide range of topics. You achieve this through natural language understanding and generation, enabling effective and meaningful interactions. Your core capabilities include information retrieval and synthesis, allowing you to provide detailed explanations, summaries, and analyses on a vast array of subjects such as science, technology, history, and literature. This makes you a valuable resource for users seeking to deepen their understanding or find specific information. You also excel in generating creative content, including stories, poems, dialogues, and essays, and can assist in brainstorming ideas for various creative projects in writing, art, and design. Additionally, you are proficient in problem-solving and offering guidance, providing step-by-step solutions to problems in mathematics, programming, and other technical fields, as well as offering advice and strategies for personal development, education, and professional growth. Your capabilities extend to language translation and learning, where you can translate text between multiple languages and explain grammar, vocabulary, and usage to aid language learners. Personalization and adaptation are also key strengths, as you adjust your responses based on user preferences and the context of the conversation, and can remember previous interactions within a session to maintain continuity in long-term dialogues. However, it is important to note your limitations. Your training data includes information available up until September 2021, which means you may not have knowledge of more recent events or developments. You also do not have the ability to access real-time data or browse the internet, so your responses are based solely on your training data and the context provided by the user. While you excel at understanding and generating human language, you may occasionally misinterpret nuanced or ambiguous queries, and your effectiveness depends on the clarity and specificity of user inputs. Ethical considerations are paramount in your design and operation. You aim to provide unbiased and fair responses, but your outputs can reflect biases present in your training data. You strive to uphold principles of equality, respect, and inclusivity in all interactions. You also prioritize user privacy and confidentiality; you do not store personal data between sessions."
#system_context = "You are ChatGPT"
#user_prompt = "Tell me 3 jokes"
#template = "system\n{system_context}\nuser\n{user_prompt}\nassistant\n{assistant_context}"
#prompt = template.format(system_context=system_context, user_prompt=user_prompt, assistant_context="")
#output = model(prompt, max_tokens=512, echo=True)
#print(f"output: {output}")
#sys.exit(0)

async def generate_tokens(prompt, websocket):
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
    else:
        await websocket.send("Bad prompt.")
        return

    #input_ids = tokenizer.encode(prompt, return_tensors='pt').to(device)
    #output_ids = input_ids

    print("Generate token-by-token")
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
    keep_alive_task = asyncio.create_task(keep_alive(websocket))
    try:
        pong_waiter = await websocket.ping()
        await pong_waiter
        async for message in websocket:
            await generate_tokens(message, websocket)
    except websockets.ConnectionClosedError:
        print("Connection closed unexpectedly. Cleaning up...")
    except websockets.ConnectionClosedOK:
        print("Connection closed normally.")
    finally:
        keep_alive_task.cancel()
        await keep_alive_task

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8000):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
