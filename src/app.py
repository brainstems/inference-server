import os

from aiohttp import web
from pymongo import MongoClient

from src.models.models import ModelSchemaBase
from src.repositories.repositories import ModelRepository
from src.services.services import ModelService

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db = client['inference_server']
model_repository = ModelRepository(db)
model_service = ModelService(model_repository)

"""
In the app.py file, create a dedicated section specifically for handling the routing of MongoDB model elements.
This involves setting up endpoints that interact with the MongoDB models, such as creating, reading, updating,
and deleting documents. By centralizing these routes in one section, we can manage the models more effectively 
and maintain cleaner code. This organization not only improves the current structure but also lays the foundation
for decoupling the models into an independent repository in the future, enhancing modularity and facilitating
easier maintenance and scalability.
"""


async def add_model_handler(request):
    """
    Adds a new model to MongoDB via an HTTP POST request.
    """
    try:
        model_data = await request.json()
        model = ModelSchemaBase(**model_data)
        model_id = model_service.add_model(model)
        return web.json_response({"message": f"Model added with ID: {model_id}"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def activate_model_handler(request):
    """
    Activates a model by ID via an HTTP PUT request.
    """
    try:
        model_id = request.match_info['model_id']
        return web.json_response({
            "message": "Model activated" if model_service.set_active_model(
                model_id) else "Model not found or activation failed"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def delete_model_handler(request):
    """
    Deletes a model by ID via an HTTP DELETE request.
    """
    try:
        model_id = request.match_info['model_id']
        return web.json_response(
            {"message": "Model deleted" if model_service.delete_model(model_id) else "Model not found"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def list_models_handler(request):
    """
    Lists all models via an HTTP GET request.
    """
    try:
        models = model_service.list_all_models()

        for model in models:
            if '_id' in model:
                model['_id'] = str(model['_id'])

        return web.json_response(models)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)
