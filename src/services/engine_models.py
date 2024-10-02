import logging
import os
import sys

import torch
import torch.multiprocessing as mp
from model_operations import generate_tokens, load_model
from transformers import AutoTokenizer
from vllm import LLM, SamplingParams

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
mp.set_start_method('spawn', force=True)


class BaseEngine:
    def __init__(self, model_metadata):
        self.model_metadata = model_metadata

    def process(self, prompt):
        raise NotImplementedError("El método 'process' debe ser implementado en las subclases")


class EngineTransformer(BaseEngine):
    def __init__(self, model_metadata):
        super().__init__(model_metadata)
        self.current_path = os.getcwd()
        logging.info(f"Current path: {self.current_path}")
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        logging.info(f"Device: {self.device}")
        local_path = f'/app/models--ai21labs--AI21-Jamba-1.5-Mini/'
        logging.info(f"Local Model Path: {local_path}")
        model_name = "ai21labs/AI21-Jamba-1.5-Mini"

        self.llm = LLM(
            # model=f'{local_path}',
            model=model_name,
            tensor_parallel_size=2,
            max_model_len=1024
        )
        logging.info(f"LLM: complete")

        self.tokenizer = AutoTokenizer.from_pretrained(
            # f'{local_path}'
            model_name
        )
        logging.info(f"Tokenizer: complete")

    def process(self, prompt):
        messages = [
            {"role": "system", "content": "You are an ancient oracle who speaks in cryptic but wise phrases."},
            # {"role": "user", "content": prompt},
            {"role": "user", "content": "Hello, what is your wisdom?"},
        ]

        logging.info(f"Message: complete")
        prompts = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
        logging.info(f"Prompts: complete")

        sampling_params = SamplingParams(temperature=0.7, top_p=0.9, max_tokens=100)
        logging.info(f"Sampling: complete")

        outputs = self.llm.generate(prompts, sampling_params)
        logging.info(f"Output: complete")

        return outputs[0].outputs[0].text


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
