from unittest.mock import patch, AsyncMock

import pytest


@pytest.mark.asyncio
@patch('src.services.services.ModelService.add_model', new_callable=AsyncMock)
async def test_add_model(mock_add_model, aiohttp_client, app):
    mock_add_model.return_value = "mock_model_id"

    client = await aiohttp_client(app)
    model_data = {
        "model_name": "test-model",
        "s3_path": "s3://test-bucket/test-model",
        "enabled": False
    }

    resp = await client.post('/models', json=model_data)
    assert resp.status == 200
    json_response = await resp.json()
    assert "Model added with ID" in json_response['message']


@pytest.mark.asyncio
@patch('src.services.services.ModelService.list_all_models', new_callable=AsyncMock)
async def test_list_models(mock_list_models, aiohttp_client, app):
    mock_list_models.return_value = [{"_id": "mock_id", "model_name": "test-model"}]

    client = await aiohttp_client(app)

    resp = await client.get('/models')
    assert resp.status == 200
    json_response = await resp.json()
    assert isinstance(json_response, list)
    assert json_response[0]['_id'] == "mock_id"


@pytest.mark.asyncio
@patch('src.services.services.ModelService.set_active_model', new_callable=AsyncMock)
async def test_activate_model(mock_set_active_model, aiohttp_client, app):
    mock_set_active_model.return_value = True

    client = await aiohttp_client(app)
    model_id = "mock_model_id"

    resp = await client.put(f'/models/{model_id}/activate')
    assert resp.status == 200
    json_response = await resp.json()
    assert "Model activated" in json_response['message']


@pytest.mark.asyncio
@patch('src.services.services.ModelService.delete_model', new_callable=AsyncMock)
async def test_delete_model(mock_delete_model, aiohttp_client, app):
    mock_delete_model.return_value = True

    client = await aiohttp_client(app)
    model_id = "mock_model_id"

    resp = await client.delete(f'/models/{model_id}')
    assert resp.status == 200
    json_response = await resp.json()
    assert "Model deleted" in json_response['message']
