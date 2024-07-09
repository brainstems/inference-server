from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)

# Ensure the model is loaded on the GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"device set to: {device}")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("cognitivecomputations/dolphin-2.0-mistral-7b")

# Load model
#model = AutoModelForCausalLM.from_pretrained("TheBloke/dolphin-2.0-mistral-7B-GGUF", model_file="dolphin-2.0-mistral-7b.Q4_K_M.gguf", model_type="mistral", gpu_layers=50, token=access_token)
model = AutoModelForCausalLM.from_pretrained("cognitivecomputations/dolphin-2.0-mistral-7b")

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')

    # Tokenize the input prompt
    inputs = tokenizer(prompt, return_tensors='pt').to('cuda:0')

    # Generate the response
    output = model.generate(**inputs, max_new_tokens=50).to('cuda:0')
    
    # Decode the generated tokens
    response = tokenizer.decode(output[0], skip_special_tokens=True)

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
