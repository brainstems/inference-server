from flask import Flask, request, jsonify
from llama_cpp import Llama

# Create a Flask object
app = Flask("Dolphin-2.6.mistral-7b server")
model = None

# Template for the prompt
template = "<|im_start|>system\n{system_context}<|im_end|>\n<|im_start|>user\n{user_prompt}<|im_end|>\n<|im_start|>assistant\n{assistant_context}<|im_end|>"

@app.route('/dolphin', methods=['POST'])
def generate_response():
    global model
    
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
            
            # Create the model if it was not previously created
            if model is None:
                # Put the location of the GGUF model here
                model_path = "./dolphin-2.6-mistral-7b.Q8_0.gguf"
                
                # Create the model
                model = Llama(model_path=model_path)
             
            # Run the model
            output = model(prompt, max_tokens=max_tokens, echo=False)
            
            # Extract the text from the model output for better readability in the JSON response
            generated_text = output['choices'][0]['text']
            
            return jsonify({"response": generated_text})

        else:
            return jsonify({"error": "Missing required parameters"}), 400

    except Exception as e:
        return jsonify({"Error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
