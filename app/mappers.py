# app/mappers.py
from typing import Dict, Any, Union, Mapping
from . import models
from . import entities

## ====================================================

def to_person_entity_from_create(request_model: models.PersonCreateRequest, generated_id: int) -> entities.PersonEntity:
    """Maps a PersonCreateRequest API model to a PersonEntity database model, including a generated ID."""
    return entities.PersonEntity(
        id=generated_id,
        first_name=request_model.first_name,
        last_name=request_model.last_name,
        age=request_model.age,
        email=request_model.email
    )

## ====================================================

def to_person_entity_from_dict(data: Union[Dict[str, Any], Mapping]) -> entities.PersonEntity:
    """Maps a dictionary (e.g., a database row) to a PersonEntity."""
    return entities.PersonEntity(**data)

## ====================================================

def to_person_response_from_entity(entity: entities.PersonEntity) -> models.PersonResponse:
    """Maps a PersonEntity database model to a PersonResponse API model."""
    return models.PersonResponse(
        id=entity.id,
        first_name=entity.first_name,
        last_name=entity.last_name,
        age=entity.age,
        email=entity.email
    )

## ====================================================

def to_update_dict_from_request(request_model: models.PersonUpdateRequest) -> Dict[str, Any]:
    """Converts a PersonUpdateRequest API model to a dictionary for database update operations.
    
    Includes only fields that were explicitly set in the request and are not None.
    """
    # First, get a dictionary of fields that were explicitly set in the request
    update_data_with_potential_nones = request_model.model_dump(exclude_unset=True)
    
    # Then, filter out any fields that have a value of None
    # This ensures that if a client explicitly sends "field": null, it's not passed to the DB update
    # unless the intention is to actually set the DB field to NULL (which this filter prevents).
    return {key: value for key, value in update_data_with_potential_nones.items() if value is not None}
