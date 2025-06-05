"""
Main application file for the People API.
"""

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app import database
from app.routes import api, health, mcp, chat

## ====================================================

# FastAPI app instance
app = FastAPI(
    title="People API - MCP Support",
    description="A simple API to manage a list of people, now refactored into modules. With MCP Support",
    version="1.0.0",
)

## ====================================================

# Database event handlers
app.add_event_handler("startup", database.connect_db)
app.add_event_handler("shutdown", database.disconnect_db)

## ====================================================

# Include the routers
app.include_router(api.router)
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(mcp.router)

## ====================================================

# Root endpoint (can be kept here or moved to its own router if preferred)
@app.get("/", tags=["Root"], summary="Redirect to API docs", response_class=RedirectResponse, include_in_schema=False)
async def read_root():
    """
    Redirects the root path to the API documentation at /docs.
    """
    return RedirectResponse(url="/docs")

## ====================================================

# To run the app (uvicorn main:app --reload):
# import uvicorn
# if __name__ == "__main__":
#     # Note: It's common to run uvicorn from the command line directly
#     # rather than embedding it here for production or complex setups.
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
