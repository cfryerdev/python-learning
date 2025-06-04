# app/routes/api.py
from typing import List

from fastapi import APIRouter, HTTPException, status

from .. import crud, models

## ====================================================

router = APIRouter(
    prefix="/people",
    tags=["People"],
    responses={404: {"description": "Not found"}},
)

## ====================================================

@router.post("/", response_model=models.PersonResponse, status_code=status.HTTP_201_CREATED, summary="Create a new person")
async def create_person_endpoint(person_data: models.PersonCreateRequest):
    """
    Creates a new person in the system.

    - **person_data**: Data for the new person to create (from API request model).
    - **Raises HTTPException (422)**: If the provided email format is invalid.
    - **Returns**: The newly created person object (API response model).
    """
    # Basic email validation example (can be more sophisticated)
    if person_data.email and "@" not in person_data.email:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid email format")
    
    # Optional: Check if email already exists (if this logic belongs in the router)
    # This kind of check might also live in the CRUD layer or be a database constraint.
    # For now, assuming basic validation here and relying on DB for uniqueness if set.

    return await crud.create_person(person_data=person_data)

## ====================================================

@router.get("/", response_model=List[models.PersonResponse], summary="Get all people")
async def read_people_endpoint(skip: int = 0, limit: int = 100):
    """
    Retrieves a list of people, with optional pagination.

    - **skip**: Number of records to skip for pagination.
    - **limit**: Maximum number of records to return.
    - **Returns**: A list of person API response models.
    """
    people_responses = await crud.get_people(skip=skip, limit=limit)
    return people_responses

## ====================================================

@router.get("/{person_id}", response_model=models.PersonResponse, summary="Get a specific person by ID")
async def read_person_endpoint(person_id: int):
    """
    Retrieves a specific person by their ID.

    - **person_id**: The ID of the person to retrieve.
    - **Raises HTTPException (404)**: If a person with the given ID is not found.
    - **Returns**: The person API response model if found.
    """
    person_response = await crud.get_person(person_id=person_id)
    if person_response is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    return person_response

## ====================================================

@router.put("/{person_id}", response_model=models.PersonResponse, summary="Update an existing person")
async def update_person_endpoint(person_id: int, person_update_input: models.PersonUpdateRequest):
    """
    Updates an existing person by their ID.

    - **person_id**: The ID of the person to update.
    - **person_update_input**: Data for updating the person (from API request model).
    - **Raises HTTPException (404)**: If a person with the given ID is not found.
    - **Returns**: The updated person API response model if found.
    """
    # The crud.update_person function now handles the check for existing person
    # and returns None if not found, or the updated PersonResponse.
    updated_person_response = await crud.update_person(person_id=person_id, person_update_data=person_update_input)
    
    if updated_person_response is None:
        # This implies the person was not found by the crud layer, or an issue occurred during update.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found or update failed")
    return updated_person_response

## ====================================================

@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a person")
async def delete_person_endpoint(person_id: int):
    """
    Deletes a person by their ID.

    - **person_id**: The ID of the person to delete.
    - **Raises HTTPException (404)**: If a person with the given ID is not found.
    - **Returns**: No content (204 No Content) if deletion is successful.
    """
    deleted_successfully = await crud.delete_person(person_id=person_id)
    if not deleted_successfully:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    # For 204 No Content, FastAPI expects no return value or return None
    return
