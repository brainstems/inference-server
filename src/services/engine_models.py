import os

import torch
from model_operations import generate_tokens, load_model
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

class BaseEngine:
    def __init__(self, model_metadata):
        self.model_metadata = model_metadata

    def process(self, prompt):
        raise NotImplementedError("El método 'process' debe ser implementado en las subclases")


class EngineTransformer:
    def __init__(self, model_metadata):
        self.model_name = model_metadata.model_name
        self.device_count = torch.cuda.device_count() if torch.cuda.is_available() else 1

        # Establece el número de GPUs a utilizar (mínimo 2 si tienes Jamba Mini)
        self.llm = LLM(model=self.model_name,
                       max_model_len=200 * 1024,
                       tensor_parallel_size=self.device_count)

        # Cargar el tokenizador del modelo Jamba
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def process(self, prompt):
        messages = [
            {"role": "system", "content": "You are an oracle who speaks in cryptic but wise phrases."},
            {"role": "user", "content": prompt}
        ]

        prompts = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)

        sampling_params = SamplingParams(temperature=0.7, top_p=0.95, max_tokens=100)

        outputs = self.llm.generate(prompts, sampling_params)
        generated_text = outputs[0].outputs[0].text

        return generated_text


class EngineLlama(BaseEngine):
    def __init__(self, model_metadata):
        super().__init__(model_metadata)
        self.current_path = os.getcwd()
        self.model = load_model(f'{self.current_path.replace("src", "model")}/{model_metadata.model_name}', n_ctx=4096)
        print("Modelo Llama cargado exitosamente.")

    async def process(self, prompt, websocket):
        async for token in generate_tokens(prompt, self.model):
            await websocket.send(token)


class EngineService:
    def __init__(self, engine_name, model_metadata):
        self.engine = self.get_engine(engine_name, model_metadata)

    def get_engine(self, engine_name, model_metadata):
        if engine_name == "transformer":
            return EngineTransformer(model_metadata)
        elif engine_name == "llama":
            return EngineLlama(model_metadata)
        else:
            raise ValueError(f"Engine '{engine_name}' no está soportado")

    def process(self, prompt, websocket=None):
        if isinstance(self.engine, EngineLlama):
            return self.engine.process(prompt, websocket)
        else:
            return self.engine.process(prompt)


if __name__ == "__main__":
    model_metadata = {
        "model_name": "ai21labs/AI21-Jamba-1.5-Mini"
    }

    engine = EngineTransformer(model_metadata)
    prompt = "Tell me something wise."
    response = engine.process(prompt)
    print(response)
