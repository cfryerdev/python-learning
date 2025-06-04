# app/plugins/get_people_plugin.py
import json
# from typing import Optional, List # List is used in crud.get_people, but not directly in this plugin's type hints for SK

from semantic_kernel.functions.kernel_function_decorator import kernel_function
from semantic_kernel.functions.kernel_parameter_metadata import KernelParameterMetadata

from .. import crud
# from .. import models # Not strictly needed as model_dump() is on the instance

## ====================================================

class GetPeoplePlugin:
    """
    Plugin for retrieving a list of people, with optional pagination.
    """

    @kernel_function(
        description="Retrieves a list of people. Supports pagination with 'skip' and 'limit'.",
        name="get_all_people"
    )
    async def get_all_people_async(
        self,
        skip: KernelParameterMetadata(
            description="Number of records to skip for pagination. Defaults to 0 if not provided.",
            name="skip",
            is_required=False,
            default_value=0,
            type="integer"
        ),
        limit: KernelParameterMetadata(
            description="Maximum number of records to return. Defaults to 100 if not provided.",
            name="limit",
            is_required=False,
            default_value=100,
            type="integer"
        )
    ) -> str:
        """
        Kernel function to retrieve a list of people.
        """
        try:
            s = int(skip) if skip is not None else 0
            l = int(limit) if limit is not None else 100

            people_response_models = await crud.get_people(skip=s, limit=l)
            return json.dumps([person.model_dump() for person in people_response_models])
        except ValueError:
            return json.dumps({"error": "Invalid skip or limit format. Must be integers."})
        except Exception as e:
            return json.dumps({"error": "Failed to retrieve people.", "details": str(e)})
