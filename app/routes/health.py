# app/routes/health.py
from fastapi import APIRouter, status

## ====================================================

router = APIRouter(
    prefix="/api",
    tags=["Health"],
    responses={404: {"description": "Not found"}},
)

## ====================================================

@router.get("/health", response_model=dict, status_code=status.HTTP_200_OK, summary="Health endpoint")
async def api_health():
    """
    Retrieves a simple health check response for the API.

    - **Returns**: A JSON object with a status message indicating the API is healthy.
    """
    return {"status": "API endpoint is healthy"}
