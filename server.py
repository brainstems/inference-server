from flask import Flask, request, jsonify
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForSequenceClassification
import torch

# Create a Flask object
app = Flask("Dolphin-2.6.mistral-7b server")
model = None
tokenizer = None

# Template for the prompt
template = "system\n{system_context}\nuser\n{user_prompt}\nassistant\n{assistant_context}"

@app.route('/dolphin', methods=['POST'])
def generate_response():
    global model
    global tokenizer
    
    try:
        data = request.get_json()

        # Check if the required fields are present in the JSON data
        if 'system_context' in data and 'user_prompt' in data and 'max_tokens' in data and 'assistant_context' in data:
            system_context = data['system_context']
            user_prompt = data['user_prompt']
            max_tokens = int(data['max_tokens'])
            assistant_context = data['assistant_context']

            # Create the prompt using the template
            prompt = template.format(system_context=system_context, user_prompt=user_prompt, assistant_context=assistant_context)
            
            # Load the model and tokenizer if not previously loaded
            if model is None:
                model_path = "./dolphin-2.0-mistral-7b.Q5_K_S.gguf"
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                model = ORTModelForSequenceClassification.from_pretrained(model_path, from_transformers=True)
                model.to("cuda")
             
            # Generate response using the model
            inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
            outputs = model.generate(**inputs, max_new_tokens=max_tokens)
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return jsonify({"response": generated_text})

        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
