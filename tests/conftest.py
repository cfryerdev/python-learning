import pytest
import pytest_asyncio
import os
from typing import AsyncGenerator, Callable, Coroutine, Any

from sqlalchemy import text

from app import database as db_module
from app import models
from app import crud
from app.entities import people # For direct table clearing

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    # Pytest-asyncio handles loop creation by default if not specified.
    # This fixture is here to be explicit or if custom loop policy is needed later.
    # For most cases with pytest-asyncio, this can be omitted unless specific
    # loop configuration is required across the session.
    # However, if other session-scoped async fixtures depend on an event loop,
    # it's good practice to define it.
    import asyncio
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def test_db_session() -> AsyncGenerator[None, None]:
    """
    Set up an in-memory SQLite database for each test function.
    Creates tables, yields, then disconnects and clears tables.
    Autouse=True ensures this runs for every test function.
    """
    # Ensure we're using an in-memory SQLite for tests for speed and isolation
    original_db_url = os.environ.get("DATABASE_URL")
    test_db_url = "sqlite+aiosqlite:///file:testdb_in_memory?mode=memory&cache=shared&uri=true"
    os.environ["DATABASE_URL"] = test_db_url  # Override for tests, use named shared in-memory DB
    
    # Clear and reload modules in the correct order
    import importlib
    import sys
    
    # First, force reload the database module to pick up the new DATABASE_URL
    importlib.reload(db_module)
    
    # Now reload the entities module to ensure tables are registered with the new metadata
    from app import entities
    importlib.reload(entities)
    
    # Connect to the database 
    await db_module.connect_db()
    
    # Force explicit table creation if needed
    if 'people' not in db_module.metadata.tables:
        print("WARNING: 'people' table not found in metadata after reload, this shouldn't happen")
    
    # Run a quick test query to verify table exists
    try:
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='people';"
        result = await db_module.database.fetch_one(query)
        if not result:
            # Table doesn't exist, create it directly
            print("WARNING: Table 'people' not found in SQLite, forcing manual creation")
            create_table_query = """CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                age INTEGER,
                email TEXT UNIQUE
            );"""
            await db_module.database.execute(create_table_query)
    except Exception as e:
        print(f"Error checking for people table: {e}")
        # Still try to create it
        create_table_query = """CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            age INTEGER,
            email TEXT UNIQUE
        );"""
        await db_module.database.execute(create_table_query)
    
    yield # Test runs here
    
    # Clear all data from tables after the test
    # This is a more robust way to ensure test isolation than dropping/recreating tables
    # especially for in-memory DBs that might persist connections.
    async with db_module.database.transaction():
        # Using raw SQL for delete as it's straightforward for clearing all rows.
        # Ensure to use the correct table name as defined in your entities/models.
        # For SQLAlchemy Core, people_table.name gives the correct table name.
        await db_module.database.execute(text(f"DELETE FROM {people.name}"))
        # If you have an autoincrementing ID and want to reset it for SQLite:
        await db_module.database.execute(text(f"DELETE FROM sqlite_sequence WHERE name='{people.name}'"))

    # Disconnect from the database
    await db_module.disconnect_db()

    # Restore original DATABASE_URL if it was set
    if original_db_url:
        os.environ["DATABASE_URL"] = original_db_url
    else:
        # If it wasn't set, ensure it's removed so subsequent non-test code
        # (if any in the same process) doesn't accidentally use the test DB URL.
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
    
    # Reload the database module again to revert to original settings or default
    importlib.reload(db_module)
    # Also reload entities to ensure it's consistent with the reloaded database module for teardown/cleanup.
    from app import entities # Ensure it's in scope if not already
    importlib.reload(entities)


@pytest_asyncio.fixture(scope="function")
async def create_person_in_db(test_db_session: None) -> Callable[..., Coroutine[Any, Any, int]]:
    """
    Provides a callable to create a person directly in the DB for test setup.
    Relies on test_db_session to ensure DB is ready.
    Returns the ID of the created person.
    """
    async def _create_person(first_name: str, last_name: str, age: int = 30, email: str = None) -> int:
        if email is None:
            # Create a unique email if not provided to avoid IntegrityErrors
            email = f"{first_name.lower()}.{last_name.lower()}@example-test.com"
        
        person_data = models.PersonCreateRequest(
            first_name=first_name, 
            last_name=last_name, 
            age=age, 
            email=email
        )
        created_person = await crud.create_person(person_data=person_data)
        return created_person.id
    
    return _create_person
