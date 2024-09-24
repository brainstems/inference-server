from unittest.mock import patch, MagicMock

import pytest

from model_mock import ModelMock
from model_operations import generate_tokens, load_model

model = ModelMock()
prompt = """
            {"user_prompt": "Tell me a joke",
            "system_context": "You are a funny friend.",
            "assistant_context": "Be funny.",
            "max_tokens" : 1000}
        """


@patch("src.model_operations.Llama")
@patch("src.model_operations.os.path.exists", return_value=True)
def test_given_mock_model_can_be_loaded(mock_exists, mock_llama):
    mock_llama_instance = MagicMock()
    mock_llama.return_value = mock_llama_instance
    mock_llama_instance.name = "mock"

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
