import os
import asyncio

import sqlalchemy
import databases

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./people.db")

# SQLAlchemy specific parts
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Database engine (used for table creation)
# For metadata.create_all(), we need a synchronous engine.
# If the main DATABASE_URL is for aiosqlite, create a sync version for DDL.
sync_database_url = DATABASE_URL
if DATABASE_URL.startswith("sqlite+aiosqlite"):
    sync_database_url = DATABASE_URL.replace("sqlite+aiosqlite", "sqlite", 1)
engine = sqlalchemy.create_engine(sync_database_url)

async def connect_db():
    """
    Connect to the database and create tables if they don't exist.
    """
    await database.connect()
    # Create tables if they don't exist (moved here from main.py startup)
    # This ensures tables are created when the DB connection is established.
    # Note: For more complex migrations, consider tools like Alembic.
    
    # Run synchronous DDL in a thread to avoid blocking the event loop
    # and to ensure compatibility with SQLAlchemy's sync engine + aiosqlite.
    def _create_tables_sync():
        with engine.connect() as connection:
            metadata.create_all(bind=connection)
            connection.commit() # Ensure DDL is committed
    
    await asyncio.to_thread(_create_tables_sync)

async def disconnect_db():
    """
    Disconnect from the database.
    """
    await database.disconnect()
