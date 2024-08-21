import os
import json
if (os.environ.get('ENV', 'PROD') == "TESTING"):
    from tests.model_mock import ModelMock
from llama_cpp import Llama

def load_model(model_path, n_ctx):
    """
    Loads a model.

    Parameters:
    model_path (string): Path to the model.
    n_ctx (int): The number of context tokens. It includes prompts.

    Returns:
    The model object.
    """
    # ToDo: Move this env check to a file operations.
    if (os.environ.get('ENV', 'PROD') == "TESTING"):
        return ModelMock()
    model = Llama(model_path=model_path, use_gpu=True, n_gpu_layers=-1,
            n_ctx = n_ctx,
            n_threads = 4,
            stop=[""])
    return model

async def generate_tokens(prompt, model):
    """
    Generates tokens from the given prompt and model.

    Parameters:
    prompt (string): The prompt.
    model (Model object): The model object.
    """
    template = "system\n{system_context}\nuser\n{user_prompt}\nassistant\n{assistant_context}"
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
    except Exception as e:
        reason = f"Error generating token: {e}"
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
            detokenized = model.detokenize([token])
            token_str = detokenized.decode("utf-8")
            # 'stop' setting param does not seem to be working when loading the model. So, we stop when start receiving empty responses.
            if token_str == "" or token_str is None:
                return
            print(token_str)
            yield token_str
        except Exception as e:
            print(f"Could not decode token: {e}")
