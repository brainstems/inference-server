# repositories.py
from bson import ObjectId
import logging
from models.models import ModelSchema


class ModelRepository:
    def __init__(self, db):
        self.collection = db['models']

    def get_active_model(self, tag: str):
        logging.info(f'Check Model: {tag}')
        result = self.collection.find_one({"enabled": True, "tag": tag})
        if result:
            logging.info(f'result: {str(result)}')
            return ModelSchema(**result)
        return None

    def add_model(self, model_data: ModelSchema):
        result = self.collection.insert_one(model_data.dict(by_alias=True))
        return str(result.inserted_id)

    def update_model(self, model_id, update_data: dict):
        result = self.collection.update_one({"_id": ObjectId(model_id)}, {"$set": update_data})
        return result.modified_count > 0

    def delete_model(self, model_id):
        result = self.collection.delete_one({"_id": ObjectId(model_id)})
        return result.deleted_count > 0
