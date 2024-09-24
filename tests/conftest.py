# conftest.py
import pytest
from aiohttp import web

from app import add_model_handler, activate_model_handler, delete_model_handler, list_models_handler


@pytest.fixture
def app():
    app = web.Application()
    app.router.add_post('/models', add_model_handler)
    app.router.add_put('/models/{model_id}/activate', activate_model_handler)
    app.router.add_delete('/models/{model_id}', delete_model_handler)
    app.router.add_get('/models', list_models_handler)
    return app
