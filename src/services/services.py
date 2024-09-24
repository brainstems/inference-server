# services.py
import os

import boto3

from models.models import ModelSchema
from repositories.repositories import ModelRepository

import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

class ModelService:
    def __init__(self, model_repository: ModelRepository):
        self.model_repository = model_repository

    def list_all_models(self):
        """
        Returns a list of all models from the database.
        """
        models = self.model_repository.collection.find()  # Fetch all models from the MongoDB collection
        return list(models)

    def get_active_model(self, tag: str):
        return self.model_repository.get_active_model(tag=tag)

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

    def download_folder_from_s3(self, s3_path, local_path):
        """
        Downloads all files from an S3 'folder' (prefix) to a local directory.
        """
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name="us-east-1"
        )

        bucket, prefix = s3_path.replace("s3://", "").split("/", 1)

        # Ensure the local path exists
        if not os.path.exists(local_path):
            os.makedirs(local_path)

        # List all the objects under the given prefix
        result = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

        if 'Contents' in result:
            for obj in result['Contents']:
                key = obj['Key']
                # Derive the file path to download
                relative_path = key[len(prefix):].lstrip('/')
                local_file_path = os.path.join(local_path, relative_path)

                # Ensure the local directories exist
                if not os.path.exists(os.path.dirname(local_file_path)):
                    os.makedirs(os.path.dirname(local_file_path))

                # Download the file
                s3.download_file(bucket, key, local_file_path)
                print(f"Downloaded: {key} to {local_file_path}")
        else:
            print(f"No objects found in {s3_path}")

    def ensure_model_exists(self, model_name, model_s3_path, engine):
        """
        Ensures the model exists locally, downloading it from S3 if necessary.
        """

        logging.info(f'Checking engine')

        if engine == "transformer":
            logging.info(f'Transformer engine selected')
            local_model_path = f"../../model/{model_name}"
            if not os.path.exists(local_model_path):
                print(f"Downloading model from {model_s3_path}")
                self.download_folder_from_s3(model_s3_path, local_model_path)
            logging.info(f'Downloaded model from {model_s3_path}')
            return local_model_path
        else:
            logging.info(f'Llama engine selected')
            local_model_path = f"../../model/{model_name}.gguf"
            if not os.path.exists(local_model_path):
                print(f"Downloading model from {model_s3_path}")
                self.download_model_from_s3(model_s3_path, local_model_path)
            logging.info(f'Downloaded model from {model_s3_path}')
            return local_model_path
