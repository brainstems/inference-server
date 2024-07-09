from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)

# Ensure the model is loaded on the GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"device set to: {device}")

# Load the model and tokenizer
model_name = "cognitivecomputations/dolphin-2.0-mistral-7b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

@app.route('/dolphin', methods=['POST'])
def generate_text():
    # Template for the prompt
    template = "system\n{system_context}\nuser\n{user_prompt}\nassistant\n{assistant_context}"

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
            
            # Encode the input prompt
            inputs = tokenizer(prompt, return_tensors='pt')

            # Generate output
            with torch.no_grad():
                outputs = model.generate(inputs['input_ids'], max_length=max_tokens, num_return_sequences=1)

            # Decode the generated text
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

            return jsonify({'generated_text': generated_text,
                            'prompt': prompt})

        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
