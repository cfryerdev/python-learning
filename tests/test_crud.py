# tests/test_crud.py
import pytest
from typing import List

from app import crud
from app import models
from app import entities # For direct DB interaction if needed, or type hints

# The test_db_session fixture from conftest.py needs to be explicitly requested
# by each test function that needs database access.

## ====================================================

@pytest.mark.asyncio
async def test_create_person(test_db_session):
    """Test creating a person successfully."""
    person_create_data = models.PersonCreateRequest(
        first_name="Testy",
        last_name="McTestFace",
        age=30,
        email="testy@example.com"
    )
    created_person_response = await crud.create_person(person_data=person_create_data)

    assert created_person_response is not None
    assert isinstance(created_person_response, models.PersonResponse)
    assert created_person_response.id is not None
    assert created_person_response.first_name == person_create_data.first_name
    assert created_person_response.last_name == person_create_data.last_name
    assert created_person_response.age == person_create_data.age
    assert created_person_response.email == person_create_data.email

    # Verify it's in the database by trying to get it
    retrieved_person = await crud.get_person(person_id=created_person_response.id)
    assert retrieved_person is not None
    assert retrieved_person.first_name == person_create_data.first_name

## ====================================================

@pytest.mark.asyncio
async def test_get_person_exists(test_db_session, create_person_in_db):
    """Test getting an existing person."""
    person_id = await create_person_in_db(first_name="Existing", last_name="Person", age=40)
    
    retrieved_person = await crud.get_person(person_id=person_id)
    assert retrieved_person is not None
    assert retrieved_person.id == person_id
    assert retrieved_person.first_name == "Existing"

## ====================================================

@pytest.mark.asyncio
async def test_get_person_not_exists(test_db_session):
    """Test getting a non-existent person."""
    retrieved_person = await crud.get_person(person_id=99999)
    assert retrieved_person is None

## ====================================================

@pytest.mark.asyncio
async def test_get_people_empty(test_db_session):
    """Test getting people when the database is empty."""
    people_list = await crud.get_people(skip=0, limit=10)
    assert isinstance(people_list, list)
    assert len(people_list) == 0

## ====================================================

@pytest.mark.asyncio
async def test_get_people_with_data(test_db_session, create_person_in_db):
    """Test getting people with pagination and data."""
    await create_person_in_db(first_name="Person", last_name="One", age=21)
    await create_person_in_db(first_name="Person", last_name="Two", age=22)
    await create_person_in_db(first_name="Person", last_name="Three", age=23)

    # Get all
    all_people = await crud.get_people(skip=0, limit=10)
    assert len(all_people) == 3
    assert all_people[0].last_name == "One"
    assert all_people[2].last_name == "Three"

    # Test pagination: skip 1, limit 1
    paginated_people = await crud.get_people(skip=1, limit=1)
    assert len(paginated_people) == 1
    assert paginated_people[0].last_name == "Two"

    # Test pagination: limit more than available
    limited_people = await crud.get_people(skip=0, limit=5)
    assert len(limited_people) == 3

    # Test pagination: skip all
    skipped_all = await crud.get_people(skip=3, limit=10)
    assert len(skipped_all) == 0

## ====================================================

@pytest.mark.asyncio
async def test_update_person_exists(test_db_session, create_person_in_db):
    """Test updating an existing person."""
    person_id = await create_person_in_db(first_name="Original", last_name="Name", age=50)
    update_data = models.PersonUpdateRequest(
        first_name="UpdatedFirst", 
        age=55, 
        email="updated@example.com"
    )

    updated_person = await crud.update_person(person_id=person_id, person_update_data=update_data)
    assert updated_person is not None
    assert updated_person.id == person_id
    assert updated_person.first_name == "UpdatedFirst" # Changed
    assert updated_person.last_name == "Name" # Unchanged, should remain
    assert updated_person.age == 55 # Changed
    assert updated_person.email == "updated@example.com" # Changed

    # Verify in DB
    retrieved_person = await crud.get_person(person_id=person_id)
    assert retrieved_person.first_name == "UpdatedFirst"
    assert retrieved_person.age == 55
    assert retrieved_person.email == "updated@example.com"

## ====================================================

@pytest.mark.asyncio
async def test_update_person_partial_update(test_db_session, create_person_in_db):
    """Test partially updating an existing person (only one field)."""
    person_id = await create_person_in_db(first_name="OriginalFN", last_name="OriginalLN", age=60, email="original@example.com")
    update_data = models.PersonUpdateRequest(last_name="UpdatedLN") # Only update last_name

    updated_person = await crud.update_person(person_id=person_id, person_update_data=update_data)
    assert updated_person is not None
    assert updated_person.id == person_id
    assert updated_person.first_name == "OriginalFN" # Unchanged
    assert updated_person.last_name == "UpdatedLN" # Changed
    assert updated_person.age == 60 # Unchanged
    assert updated_person.email == "original@example.com" # Unchanged

## ====================================================

@pytest.mark.asyncio
async def test_update_person_no_actual_change(test_db_session, create_person_in_db):
    """Test updating with an empty update request (no fields to change)."""
    person_id = await create_person_in_db(first_name="NoChange", last_name="Person", age=70)
    update_data = models.PersonUpdateRequest() # Empty update request

    updated_person = await crud.update_person(person_id=person_id, person_update_data=update_data)
    assert updated_person is not None
    assert updated_person.first_name == "NoChange"
    assert updated_person.last_name == "Person"
    assert updated_person.age == 70

## ====================================================

@pytest.mark.asyncio
async def test_update_person_not_exists(test_db_session):
    """Test updating a non-existent person."""
    update_data = models.PersonUpdateRequest(first_name="Ghost")
    updated_person = await crud.update_person(person_id=99999, person_update_data=update_data)
    assert updated_person is None

## ====================================================

@pytest.mark.asyncio
async def test_delete_person_exists(test_db_session, create_person_in_db):
    """Test deleting an existing person."""
    person_id = await create_person_in_db(first_name="ToDelete", last_name="User")
    
    delete_result = await crud.delete_person(person_id=person_id)
    assert delete_result is True

    # Verify it's gone
    retrieved_person = await crud.get_person(person_id=person_id)
    assert retrieved_person is None

## ====================================================

@pytest.mark.asyncio
async def test_delete_person_not_exists(test_db_session):
    """Test deleting a non-existent person."""
    delete_result = await crud.delete_person(person_id=99999)
    assert delete_result is False
