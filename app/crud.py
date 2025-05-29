# app/crud.py
from typing import List, Optional
from sqlalchemy.sql import select, insert, update, delete

from . import database
from . import entities
from . import models
from . import mappers

async def _get_person_entity(person_id: int) -> Optional[entities.PersonEntity]:
    """Internal helper to fetch a person by ID and map to PersonEntity."""
    query = select(entities.people).where(entities.people.c.id == person_id)
    db_row = await database.database.fetch_one(query)
    if db_row:
        return mappers.to_person_entity_from_dict(db_row)
    return None

async def create_person(person_data: models.PersonCreateRequest) -> models.PersonResponse:
    """
    Creates a new person in the database using data from PersonCreateRequest.

    Args:
        person_data (models.PersonCreateRequest): The person data from the API request.

    Returns:
        models.PersonResponse: The created person data, including its database ID, as an API response model.
    """
    insert_query = insert(entities.people).values(
        first_name=person_data.first_name,
        last_name=person_data.last_name,
        age=person_data.age,
        email=person_data.email
    )
    last_record_id = await database.database.execute(insert_query)
    
    # Fetch the newly created record to get all its data for the response
    created_person_entity = await _get_person_entity(last_record_id)
    if not created_person_entity: # Should ideally not happen if insert was successful
        raise Exception(f"Failed to retrieve person with id {last_record_id} after creation.")
    
    return mappers.to_person_response_from_entity(created_person_entity)

async def get_person(person_id: int) -> Optional[models.PersonResponse]:
    """
    Retrieves a specific person by their ID and returns it as an API response model.

    Args:
        person_id (int): The ID of the person to retrieve.

    Returns:
        Optional[models.PersonResponse]: The person API model if found, otherwise None.
    """
    person_entity = await _get_person_entity(person_id)
    if person_entity:
        return mappers.to_person_response_from_entity(person_entity)
    return None

async def get_people(skip: int = 0, limit: int = 100) -> List[models.PersonResponse]:
    """
    Retrieves a list of people, with optional pagination, as API response models.

    Args:
        skip (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return.

    Returns:
        List[models.PersonResponse]: A list of person API models.
    """
    query = select(entities.people).offset(skip).limit(limit)
    db_results = await database.database.fetch_all(query)
    
    response_list: List[models.PersonResponse] = []
    for db_row in db_results:
        entity = mappers.to_person_entity_from_dict(db_row)
        response_list.append(mappers.to_person_response_from_entity(entity))
    return response_list

async def update_person(person_id: int, person_update_data: models.PersonUpdateRequest) -> Optional[models.PersonResponse]:
    """
    Updates an existing person by their ID using data from PersonUpdateRequest.

    Args:
        person_id (int): The ID of the person to update.
        person_update_data (models.PersonUpdateRequest): The person data from the API request for update.

    Returns:
        Optional[models.PersonResponse]: The updated person API model if found and updated, otherwise None.
    """
    existing_entity = await _get_person_entity(person_id)
    if not existing_entity:
        return None # Person not found

    update_values = mappers.to_update_dict_from_request(person_update_data)
    if not update_values: # No actual data provided for update
        return mappers.to_person_response_from_entity(existing_entity) # Return current state

    update_query = (
        update(entities.people)
        .where(entities.people.c.id == person_id)
        .values(**update_values)
    )
    await database.database.execute(update_query)
    
    updated_person_entity = await _get_person_entity(person_id)
    if not updated_person_entity: # Should not happen if update was on existing ID
        return None
        
    return mappers.to_person_response_from_entity(updated_person_entity)

async def delete_person(person_id: int) -> bool:
    """
    Deletes a person by ID.

    Args:
        person_id (int): The ID of the person to delete.

    Returns:
        bool: True if deleted, False if not found.
    """
    existing_entity = await _get_person_entity(person_id)
    if not existing_entity:
        return False
        
    delete_query = delete(entities.people).where(entities.people.c.id == person_id)
    await database.database.execute(delete_query)
    return True
