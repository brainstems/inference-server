# services.py
from src.models.models import ModelSchema

from src.repositories.repositories import ModelRepository


class ModelService:
    def __init__(self, model_repository: ModelRepository):
        self.model_repository = model_repository

    def list_all_models(self):
        """
        Returns a list of all models from the database.
        """
        models = self.model_repository.collection.find()  # Fetch all models from the MongoDB collection
        return list(models)

    def get_active_model(self):
        return self.model_repository.get_active_model()

    def set_active_model(self, model_id: str):
        self.model_repository.collection.update_many({"enabled": True}, {"$set": {"enabled": False}})
        return self.model_repository.update_model(model_id, {"enabled": True})

    def add_model(self, model_data: ModelSchema):
        return self.model_repository.add_model(model_data)

    def delete_model(self, model_id: str):
        return self.model_repository.delete_model(model_id)
