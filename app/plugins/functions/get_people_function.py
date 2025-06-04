# app/plugins/get_people_plugin.py
import json
import logging # Added

from semantic_kernel.functions.kernel_parameter_metadata import KernelParameterMetadata

from app import crud

logger = logging.getLogger(__name__) # Added

## ====================================================

class GetPeopleFunction:
    """
    Plugin for retrieving a list of people, with optional pagination.
    """

    async def get_all_people_async(
        self,
        skip: int,  # Now receives a definite integer
        limit: int  # Now receives a definite integer
    ) -> list: # Changed return type hint to list
        """
        Kernel function to retrieve a list of people.
        """
        logger.debug(f"GetPeopleFunction.get_all_people_async called with skip={skip}, limit={limit}")
        try:
            # skip and limit are now guaranteed to be integers by the caller (PeopleCRUDPlugin)
            s = skip
            l = limit
            logger.debug(f"Using skip={s}, limit={l} for CRUD operation")

            people_response_models = await crud.get_people(skip=s, limit=l)
            logger.debug(f"crud.get_people returned: {type(people_response_models)}")
            
            if not isinstance(people_response_models, list):
                logger.error(f"crud.get_people did not return a list, but: {type(people_response_models)}")
                # This will be caught by the generic Exception handler below, which is fine.
                raise TypeError(f"Expected list from crud.get_people, got {type(people_response_models)}")

            dumped_models = [person.model_dump() for person in people_response_models]
            logger.debug("Successfully model_dumped all person objects.")
            
            logger.debug("Returning list of model_dumped objects.")
            return dumped_models # Changed: return the list directly
            
        except ValueError as ve:
            logger.error(f"ValueError in GetPeopleFunction: {ve}", exc_info=True)
            # Return a dict, FastAPI will JSON encode it
            return {"error": "Invalid skip or limit format. Must be integers.", "details": str(ve)}
        except Exception as e:
            logger.error(f"Unhandled exception in GetPeopleFunction.get_all_people_async: {type(e).__name__} - {str(e)}", exc_info=True)
            
            error_details = "An unexpected error occurred."
            try:
                error_details = str(e)
                if not isinstance(error_details, str):
                    error_details = "Error object could not be converted to string."
            except Exception as str_e:
                logger.error(f"Failed to convert original exception to string: {type(str_e).__name__} - {str(str_e)}", exc_info=True)
                error_details = "Failed to get error details due to a secondary error."

            error_payload = {
                "error": "Failed to retrieve people.",
                "details": error_details[:1000] # Truncate to be safe
            }
            
            try:
                # Return a dict, FastAPI will JSON encode it
                return error_payload
            except Exception as dump_e: # This inner try-except might be less necessary if error_payload is simple
                logger.critical(f"CRITICAL: Failed to prepare error payload: {type(dump_e).__name__} - {str(dump_e)}", exc_info=True)
                # Fallback to a simple dict that FastAPI can serialize
                return {"error": "Critical error during error reporting. Check server logs."}
