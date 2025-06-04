# app/plugins/delete_person_plugin.py
import json

from semantic_kernel.functions.kernel_parameter_metadata import KernelParameterMetadata

from app import crud

## ====================================================

class DeletePersonFunction:
    """
    Plugin for deleting a person by their ID.
    """

    async def delete_person_by_id_async(
        self,
        person_id: KernelParameterMetadata(
            description="The unique ID of the person to delete.",
            name="person_id",
            is_required=True,
            type="integer"
        )
    ) -> str:
        """
        Kernel function to delete a person by ID.
        """
        try:
            pid = int(person_id)
            deleted_successfully = await crud.delete_person(person_id=pid)
            if deleted_successfully:
                return json.dumps({"status": "Person deleted successfully.", "person_id": pid})
            else:
                return json.dumps({"error": "Person not found, could not delete.", "person_id": pid})
        except ValueError:
            return json.dumps({"error": "Invalid person_id format. Must be an integer.", "person_id_received": str(person_id)})
        except Exception as e:
            return json.dumps({"error": "Failed to delete person.", "details": str(e)})
