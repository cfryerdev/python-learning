# app/plugins/people_crud_plugin.py
from typing import Optional, Union # Added Union # Added
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_parameter_metadata import KernelParameterMetadata
from .functions.create_person_function import CreatePersonFunction
from .functions.get_person_function import GetPersonFunction
from .functions.get_people_function import GetPeopleFunction
from .functions.update_person_function import UpdatePersonFunction
from .functions.delete_person_function import DeletePersonFunction

class PeopleCRUDPlugin:
    """Container for all people CRUD operations."""
    def __init__(self):
        self.create_plugin = CreatePersonFunction()
        self.get_person_plugin = GetPersonFunction()
        self.get_people_plugin = GetPeopleFunction()
        self.update_plugin = UpdatePersonFunction()
        self.delete_plugin = DeletePersonFunction()
        
    ## ====================================================
    
    @kernel_function(
        description="Creates a new person in the system. "
                    "The input must be a JSON string representing the person's data, "
                    "including 'first_name' (string, required), 'last_name' (string, required), "
                    "'age' (integer, optional), and 'email' (string, optional, must be unique if provided).",
        name="create_person"
    )
    async def create_person(self, person_data_json):
        """Creates a new person in the system."""
        return await self.create_plugin.create_person_from_json_async(person_data_json)
    
    ## ====================================================

    @kernel_function(
        description="Retrieves a specific person by their unique ID.",
        name="get_person_by_id"
    )
    async def get_person_by_id(self, person_id):
        """Retrieves a specific person by their unique ID."""
        return await self.get_person_plugin.get_person_by_id_async(person_id)
    
    ## ====================================================
    
    @kernel_function(
        description="Retrieves a list of people. Supports pagination with 'skip' and 'limit'.",
        name="get_all_people"
        # 'parameters' argument removed as it's not supported by @kernel_function decorator
    )
    async def get_all_people(
        self,
        skip: Optional[int] = 0,  
        limit: Optional[int] = 100 
    ) -> Union[list, dict]:
        """Retrieves a list of all people with pagination support.

        Args:
            skip (Optional[int]): Number of records to skip for pagination. Defaults to 0.
            limit (Optional[int]): Maximum number of records to return. Defaults to 100.
        """
        # Handle cases where 'skip' or 'limit' might be explicitly passed as None by the client
        actual_skip = skip if skip is not None else 0 
        actual_limit = limit if limit is not None else 100
        return await self.get_people_plugin.get_all_people_async(actual_skip, actual_limit)
    
    ## ====================================================
    
    @kernel_function(
        description="Updates an existing person by their unique ID. "
                    "Requires the person's ID and a JSON string of fields to update. "
                    "Fields can include 'first_name', 'last_name', 'age', 'email'. All fields are optional in the update data.",
        name="update_person_by_id"
    )
    async def update_person_by_id(self, person_id, person_update_data_json):
        """Updates an existing person by their unique ID."""
        return await self.update_plugin.update_person_by_id_async(person_id, person_update_data_json)
    
    ## ====================================================
    
    @kernel_function(
        description="Deletes a person by their unique ID.",
        name="delete_person_by_id"
    )
    async def delete_person_by_id(self, person_id):
        """Deletes a person by their unique ID."""
        return await self.delete_plugin.delete_person_by_id_async(person_id)
