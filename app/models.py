# app/models.py
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class PersonBaseModel(BaseModel):
    """Base model for person attributes, used for sharing common fields."""
    first_name: str = Field(..., min_length=1, max_length=50, description="Person's first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Person's last name")
    age: Optional[int] = Field(None, ge=0, le=150, description="Person's age")
    email: Optional[str] = Field(None, max_length=100, description="Person's email address, must be unique if provided")

class PersonCreateRequest(PersonBaseModel):
    """Model for creating a new person. Inherits all fields from PersonBaseModel."""
    # This class currently inherits all fields and behavior from PersonBaseModel
    # without adding new fields or overriding existing ones. It serves as a specific
    # type hint for creation requests.
    # Specific validation for creation can be added here if needed.
    # For example, making email mandatory on create:
    # email: str = Field(..., max_length=100, description="Person's email address")

class PersonUpdateRequest(BaseModel):
    """Model for updating an existing person. All fields are optional."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Person's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Person's last name")
    age: Optional[int] = Field(None, ge=0, le=150, description="Person's age")
    email: Optional[str] = Field(None, max_length=100, description="Person's email address, must be unique if provided")

class PersonResponse(PersonBaseModel):
    """Model for API responses when returning person data."""
    id: int = Field(..., description="Unique identifier for the person")
    model_config = ConfigDict(from_attributes=True)
