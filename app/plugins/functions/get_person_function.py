# app/plugins/get_person_plugin.py
import json

from semantic_kernel.functions.kernel_parameter_metadata import KernelParameterMetadata

from app import crud

## ====================================================

class GetPersonFunction:
    """
    Plugin for retrieving a specific person by their ID.
    """

    async def get_person_by_id_async(
        self,
        person_id: KernelParameterMetadata(
            description="The unique ID of the person to retrieve.",
            name="person_id",
            is_required=True,
            type="integer"
        )
    ) -> str:
        """
        Kernel function to retrieve a person by ID.
        """
        try:
            pid = int(person_id) 
            person_response_model = await crud.get_person(person_id=pid)
            if person_response_model:
                return json.dumps(person_response_model.model_dump())
            else:
                return json.dumps({"error": "Person not found.", "person_id": pid})
        except ValueError:
            return json.dumps({"error": "Invalid person_id format. Must be an integer.", "person_id_received": str(person_id)})
        except Exception as e:
            return json.dumps({"error": "Failed to retrieve person.", "details": str(e)})
