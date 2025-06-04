# app/plugins/create_person_plugin.py
import json
# from typing import Optional, List # Not strictly needed for this specific plugin

from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_parameter_metadata import KernelParameterMetadata

from .. import crud
from .. import models

## ====================================================

class CreatePersonPlugin:
    """
    Plugin for creating a new person in the system.
    The LLM can use this to add new people to the database.
    """

    @kernel_function(
        description="Creates a new person in the system. "
                    "The input must be a JSON string representing the person's data, "
                    "including 'first_name' (string, required), 'last_name' (string, required), "
                    "'age' (integer, optional), and 'email' (string, optional, must be unique if provided).",
        name="create_person"
    )
    async def create_person_from_json_async(
        self,
        person_data_json: KernelParameterMetadata(
            description="A JSON string with the person's details. "
                        "Example: '{\"first_name\": \"John\", \"last_name\": \"Doe\", \"age\": 30, \"email\": \"john.doe@example.com\"}'",
            name="person_data_json",
            is_required=True,
            type="string"
        )
    ) -> str:
        """
        Kernel function to create a new person using JSON data.
        """
        try:
            person_data_dict = json.loads(person_data_json)
            person_create_request = models.PersonCreateRequest(**person_data_dict)
            created_person_response_model = await crud.create_person(person_data=person_create_request)
            return json.dumps(created_person_response_model.model_dump())
        except json.JSONDecodeError as e:
            return json.dumps({"error": "Invalid JSON input provided.", "details": str(e)})
        except Exception as e: 
            return json.dumps({"error": "Failed to create person.", "details": str(e)})
