# tests/test_mappers.py
import pytest
from typing import Optional

from app import models
from app import entities
from app import mappers

## ====================================================

def test_to_person_entity_from_create():
    """Test mapping PersonCreateRequest to PersonEntity."""
    request_model = models.PersonCreateRequest(
        first_name="Test",
        last_name="User",
        age=30,
        email="test.user@example.com"
    )
    generated_id = 123

    entity = mappers.to_person_entity_from_create(request_model, generated_id)

    assert isinstance(entity, entities.PersonEntity)
    assert entity.id == generated_id
    assert entity.first_name == request_model.first_name
    assert entity.last_name == request_model.last_name
    assert entity.age == request_model.age
    assert entity.email == request_model.email

## ====================================================

def test_to_person_entity_from_dict():
    """Test mapping a dictionary (e.g., from DB) to PersonEntity."""
    db_row_dict = {
        "id": 1,
        "first_name": "Jane",
        "last_name": "Doe",
        "age": 28,
        "email": "jane.doe@example.com"
    }

    entity = mappers.to_person_entity_from_dict(db_row_dict)

    assert isinstance(entity, entities.PersonEntity)
    assert entity.id == db_row_dict["id"]
    assert entity.first_name == db_row_dict["first_name"]
    assert entity.last_name == db_row_dict["last_name"]
    assert entity.age == db_row_dict["age"]
    assert entity.email == db_row_dict["email"]

## ====================================================

def test_to_person_entity_from_dict_with_optional_nulls():
    """Test mapping a dictionary with None values for optional fields."""
    db_row_dict = {
        "id": 2,
        "first_name": "John",
        "last_name": "Smith",
        "age": None,
        "email": None
    }

    entity = mappers.to_person_entity_from_dict(db_row_dict)

    assert isinstance(entity, entities.PersonEntity)
    assert entity.id == db_row_dict["id"]
    assert entity.first_name == db_row_dict["first_name"]
    assert entity.last_name == db_row_dict["last_name"]
    assert entity.age is None
    assert entity.email is None

## ====================================================

def test_to_person_response_from_entity():
    """Test mapping PersonEntity to PersonResponse."""
    person_entity = entities.PersonEntity(
        id=10,
        first_name="Alice",
        last_name="Wonderland",
        age=25,
        email="alice.wonder@example.com"
    )

    response_model = mappers.to_person_response_from_entity(person_entity)

    assert isinstance(response_model, models.PersonResponse)
    assert response_model.id == person_entity.id
    assert response_model.first_name == person_entity.first_name
    assert response_model.last_name == person_entity.last_name
    assert response_model.age == person_entity.age
    assert response_model.email == person_entity.email

## ====================================================

def test_to_update_dict_from_request_all_fields():
    """Test mapping PersonUpdateRequest to a dictionary for DB update (all fields)."""
    update_request = models.PersonUpdateRequest(
        first_name="UpdatedFirst",
        last_name="UpdatedLast",
        age=40,
        email="updated.email@example.com"
    )

    update_dict = mappers.to_update_dict_from_request(update_request)

    expected_dict = {
        "first_name": "UpdatedFirst",
        "last_name": "UpdatedLast",
        "age": 40,
        "email": "updated.email@example.com"
    }
    assert update_dict == expected_dict

## ====================================================

def test_to_update_dict_from_request_some_fields_none():
    """Test mapping PersonUpdateRequest with some None fields."""
    update_request = models.PersonUpdateRequest(
        first_name="UpdatedFirstOnly",
        last_name=None, # This field should be excluded
        age=45,
        email=None # This field should be excluded
    )

    update_dict = mappers.to_update_dict_from_request(update_request)

    expected_dict = {
        "first_name": "UpdatedFirstOnly",
        "age": 45,
    }
    assert update_dict == expected_dict

## ====================================================

def test_to_update_dict_from_request_all_fields_none():
    """Test mapping PersonUpdateRequest with all fields None (empty update)."""
    update_request = models.PersonUpdateRequest(
        first_name=None,
        last_name=None,
        age=None,
        email=None
    )

    update_dict = mappers.to_update_dict_from_request(update_request)

    expected_dict = {}
    assert update_dict == expected_dict

## ====================================================

def test_to_update_dict_from_request_no_fields_provided():
    """Test mapping an empty PersonUpdateRequest (no fields explicitly provided)."""
    # Pydantic models created with no arguments will have fields set to their defaults (often None for Optional fields)
    update_request = models.PersonUpdateRequest()

    update_dict = mappers.to_update_dict_from_request(update_request)
    
    # Depending on Pydantic version and model definition (default values vs. Optional without defaults):
    # If fields default to None and are not explicitly provided, they are treated as None.
    # The mapper correctly excludes them.
    expected_dict = {}
    assert update_dict == expected_dict
