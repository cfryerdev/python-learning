# app/plugins/update_person_plugin.py
import json

from semantic_kernel.functions.kernel_parameter_metadata import KernelParameterMetadata

from app import crud
from app import models

## ====================================================

class UpdatePersonFunction:
    """
    Plugin for updating an existing person by their ID.
    """

    async def update_person_by_id_async(
        self,
        person_id: KernelParameterMetadata(
            description="The unique ID of the person to update.",
            name="person_id",
            is_required=True,
            type="integer"
        ),
        person_update_data_json: KernelParameterMetadata(
            description="A JSON string with the person's details to update. "
                        "Example: '{\"first_name\": \"Jane\", \"email\": \"jane.doe@example.com\"}'",
            name="person_update_data_json",
            is_required=True,
            type="string"
        )
    ) -> str:
        """
        Kernel function to update a person using JSON data.
        """
        try:
            pid = int(person_id)
            update_data_dict = json.loads(person_update_data_json)
            person_update_request = models.PersonUpdateRequest(**update_data_dict)
            
            updated_person_response_model = await crud.update_person(person_id=pid, person_update_data=person_update_request)
            
            if updated_person_response_model:
                return json.dumps(updated_person_response_model.model_dump())
            else:
                return json.dumps({"error": "Person not found or update failed.", "person_id": pid})
        except json.JSONDecodeError as e:
            return json.dumps({"error": "Invalid JSON input for update data.", "details": str(e)})
        except ValueError:
            return json.dumps({"error": "Invalid person_id format. Must be an integer.", "person_id_received": str(person_id)})
        except Exception as e:
            return json.dumps({"error": "Failed to update person.", "details": str(e)})
