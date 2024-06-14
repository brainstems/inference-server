from llama_cpp import Llama

# Directory containing the model and config files
model_path = "./dolphin-2.6-mistral-7b.Q8_0.gguf"

# Create a llama model
model = Llama(model_path=model_path)

# Prompt creation
system_message = "You are a helpful assistant"
user_message = "Generate a list of 5 funny dog names"

prompt = f"""<s>[INST] <<SYS>>
{system_message}
<</SYS>>
{user_message} [/INST]"""

# Model parameters
max_tokens = 100

# Run the model
output = model(prompt, max_tokens=max_tokens, echo=True)

# Print the model output
print(output)
