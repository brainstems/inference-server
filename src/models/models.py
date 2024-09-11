from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field=None, config=None):
        """
        Validate the given value as a valid ObjectId.
        """
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        """
        Update the JSON schema to represent ObjectId as a string.
        """
        schema.update(type='string')
        return schema


class ModelSchemaBase(BaseModel):
    model_name: Optional[str]
    s3_path: str
    enabled: bool

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ModelSchema(ModelSchemaBase):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
