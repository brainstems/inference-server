# services.py
import os

import boto3

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

    def download_model_from_s3(self, s3_path, local_path):
        """
        Downloads the model from S3 if it's not already present locally.
        """
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name="us-east-1"
        )
        bucket, key = s3_path.replace("s3://", "").split("/", 1)
        s3.download_file(bucket, key, local_path)

    def ensure_model_exists(self, model_name, model_s3_path):
        """
        Ensures the model exists locally, downloading it from S3 if necessary.
        """
        local_model_path = f"../../model/{model_name}.gguf"
        if not os.path.exists(local_model_path):
            print(f"Downloading model from {model_s3_path}")
            self.download_model_from_s3(model_s3_path, local_model_path)
        return local_model_path
