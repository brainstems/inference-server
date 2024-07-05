from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)

# Load the model and tokenizer
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Ensure the model is loaded on the GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"device set to: {device}")
model = AutoModelForCausalLM.from_pretrained(model_name).to(device)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    input_text = data.get('input_text', '')

    # Tokenize input text
    inputs = tokenizer(input_text, return_tensors='pt').to(device)

    # Generate text
    with torch.no_grad():
        outputs = model.generate(inputs['input_ids'], max_length=100)

    # Decode the generated text
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return jsonify({'generated_text': generated_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
