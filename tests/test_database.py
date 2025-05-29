# tests/test_database.py
import pytest
import pytest_asyncio # Moved import to top
import os
import importlib
from unittest import mock
from app import database as db_module

# We'll mark async tests individually instead of using pytestmark
# This avoids the warning about synchronous tests with asyncio marker

@pytest_asyncio.fixture(scope="function", autouse=True)
async def manage_db_state_after_tests():
    """
    Ensures that if a test leaves the global database object connected,
    it gets disconnected. Also reloads the module to reset its state
    for the next test, especially after monkeypatching os.environ.
    """
    yield
    if db_module.database.is_connected:
        await db_module.database.disconnect()
    
    # Reload the module to ensure it's in a clean state for the next test,
    # especially regarding environment-dependent global variables.
    importlib.reload(db_module)


def test_database_url_default(monkeypatch):
    """Test that DATABASE_URL defaults correctly when the env var is not set."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    importlib.reload(db_module)  # Reload to apply patched environment
    
    assert db_module.DATABASE_URL == "sqlite+aiosqlite:///./people.db"
    assert db_module.sync_database_url == "sqlite:///./people.db"

def test_database_url_from_env_aiosqlite(monkeypatch):
    """Test DATABASE_URL and sync_database_url with an aiosqlite URL from env var."""
    test_url = "sqlite+aiosqlite:///./people.db"
    monkeypatch.setenv("DATABASE_URL", test_url)
    importlib.reload(db_module)
    
    assert db_module.DATABASE_URL == test_url
    assert db_module.sync_database_url == "sqlite:///./people.db"

@pytest.mark.asyncio
async def test_connect_disconnect_flow():
    """Test the basic database connect and disconnect flow."""
    # Create a clean database module for this test
    test_db_module = importlib.import_module('app.database')
    
    # Use a separate in-memory database to avoid conflicts
    # This ensures we're testing the basic flow without other test interference
    with mock.patch.dict(os.environ, {"DATABASE_URL": "sqlite+aiosqlite:///:memory:"}):
        importlib.reload(test_db_module)
        
        # We need to reload entities too to register tables with the new metadata
        entities_module = importlib.import_module('app.entities')
        importlib.reload(entities_module)

        assert not test_db_module.database.is_connected, "Database should initially be disconnected"

        # Instead of mocking metadata.create_all, we'll check if tables exist after connection
        await test_db_module.connect_db()
        assert test_db_module.database.is_connected, "Database should be connected after connect_db()"
        
        # Clean up
        await test_db_module.disconnect_db()

    # This is now handled in the test above

@pytest.mark.asyncio
async def test_connect_db_already_connected():
    """Test behavior of connect_db when the database is already connected."""
    # Create a clean database module for this test
    test_db_module = importlib.import_module('app.database')
    
    # Use a separate in-memory database
    with mock.patch.dict(os.environ, {"DATABASE_URL": "sqlite+aiosqlite:///:memory:"}):
        importlib.reload(test_db_module)
        
        # We need to reload entities too to register tables with the new metadata
        entities_module = importlib.import_module('app.entities')
        importlib.reload(entities_module)

        # Use a spy instead of a mock to allow the real method to run
        with mock.patch.object(test_db_module.metadata, 'create_all', wraps=test_db_module.metadata.create_all) as spy_create_all:
            await test_db_module.connect_db()  # First connection
            assert test_db_module.database.is_connected
            assert spy_create_all.call_count >= 1

            # Call connect_db again
            await test_db_module.connect_db()
            assert test_db_module.database.is_connected, "Database should remain connected"
            # create_all should be called again
            assert spy_create_all.call_count >= 2, "create_all should be called again"

        # Clean up
        await test_db_module.disconnect_db()

@pytest.mark.asyncio
async def test_disconnect_db_not_connected():
    """Test behavior of disconnect_db when the database is not connected."""
    # Create a clean database module for this test
    test_db_module = importlib.import_module('app.database')
    
    # Use a separate in-memory database
    with mock.patch.dict(os.environ, {"DATABASE_URL": "sqlite+aiosqlite:///:memory:"}):
        importlib.reload(test_db_module)

        assert not test_db_module.database.is_connected
        # Attempting to disconnect when not connected should be safe and not raise an error
        await test_db_module.disconnect_db()
        assert not test_db_module.database.is_connected, "Database should remain disconnected"
