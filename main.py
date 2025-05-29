"""
Main application file for the People API.
"""
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app import database  # Assuming database.py has connect_db and disconnect_db
from app import routes # Assuming routes.py has a router instance

# Load environment variables from .env file
load_dotenv()

# FastAPI app instance
app = FastAPI(
    title="People API - Refactored",
    description="A simple API to manage a list of people, now refactored into modules.",
    version="0.2.0",
)

# Database event handlers
app.add_event_handler("startup", database.connect_db)
app.add_event_handler("shutdown", database.disconnect_db)

# Include the routers
app.include_router(routes.router)

# Root endpoint (can be kept here or moved to its own router if preferred)
@app.get("/", tags=["Root"], summary="Redirect to API docs", response_class=RedirectResponse)
async def read_root():
    """
    Redirects the root path to the API documentation at /docs.
    """
    return RedirectResponse(url="/docs")

# To run the app (uvicorn main:app --reload):
# import uvicorn
# if __name__ == "__main__":
#     # Note: It's common to run uvicorn from the command line directly
#     # rather than embedding it here for production or complex setups.
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
