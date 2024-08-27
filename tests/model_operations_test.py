import pytest
from model_mock import ModelMock

from src.model_operations import generate_tokens, load_model

model = ModelMock()
prompt = """
            {"user_prompt": "Tell me a joke",
            "system_context": "You are a funny friend.",
            "assistant_context": "Be funny.",
            "max_tokens" : 1000}
        """


def test_given_mock_model_can_be_loaded():
    model = load_model("path1", 1)
    assert model.name == "mock"


def test_iterable_mock():
    mock = ModelMock()
    for w in mock:
        assert w is not None


@pytest.mark.asyncio
async def test_given_mock_model_returns_token_by_token():
    assert model.name == "mock"
    index = 1
    async for token in generate_tokens(prompt, model):
        assert token == f"['token{index}']"
        index += 1
