import os

from transformers import AutoTokenizer, AutoModelForCausalLM

from src.model_operations import generate_tokens, load_model


class BaseEngine:
    def __init__(self, model_metadata):
        self.model_metadata = model_metadata

    def process(self, prompt):
        raise NotImplementedError("El método 'process' debe ser implementado en las subclases")


class EngineTransformer(BaseEngine):
    def __init__(self, model_metadata):
        super().__init__(model_metadata)
        self.current_path = os.getcwd()
        self.tokenizer = AutoTokenizer.from_pretrained(
            f'{self.current_path.replace("src", "model")}/{model_metadata.model_name}')
        self.model = AutoModelForCausalLM.from_pretrained(
            f'{self.current_path.replace("src", "model")}/{model_metadata.model_name}')

    def process(self, prompt):
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(inputs['input_ids'], max_new_tokens=100)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response


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

#
# if __name__ == "__main__":
#     model_metadata_transformer = {
#         "model_name": "ai21labs/AI21-Jamba-1.5-Mini"
#     }
#
#     model_metadata_llama = {
#         "model_path": "ruta_al_modelo_llama"
#     }
#
#     service = EngineService("transformer", model_metadata_transformer)
#     prompt = "¿Cuál es el futuro de la inteligencia artificial?"
#     respuesta = service.process(prompt)
#     print("Respuesta generada (Transformer):", respuesta)
