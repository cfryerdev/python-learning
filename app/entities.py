# app/entities.py
from typing import Optional
import sqlalchemy

from pydantic import BaseModel
from .database import metadata

## ====================================================

# Define the 'people' table using the metadata from database.py
people = sqlalchemy.Table(
    "people",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("first_name", sqlalchemy.String, index=True),
    sqlalchemy.Column("last_name", sqlalchemy.String, index=True),
    sqlalchemy.Column("age", sqlalchemy.Integer, nullable=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True, index=True, nullable=True),
    extend_existing=True
)

## ====================================================

class PersonEntity(BaseModel):
    """Pydantic model representing the 'people' table structure for internal use."""
    id: int
    first_name: str
    last_name: str
    age: Optional[int] = None
    email: Optional[str] = None

    model_config = {"from_attributes": True}
