# Solution Overview and Project Structure

This document provides an overview of the project structure, detailing the purpose of key directories and files.

## Project Tree View

```
.
├── .docs/                                  # Project documentation and design documents
│   ├── AGENTIC.md                          # Description of agentic microservices concept
│   ├── ARCHITECTURE.md                     # Overview of the system architecture
│   ├── FUNCTIONS.md                        # Detailed description of key functions
│   ├── INTEGRATION.md                      # Guide for integrating MCP with AI platforms
│   ├── LEARNING.md                         # Notes and learnings during development
│   ├── LLM.md                              # Documentation for LLM integration
│   ├── MCP.md                              # Model Context Protocol documentation
│   └── SOLUTION.md                         # This file: project structure and overview
├── .env                                    # Environment variables (e.g., database URL, API keys) (Gitignored)
├── .venv/                                  # Python virtual environment directory (Gitignored)
├── README.md                               # Main project documentation, setup, and usage instructions
├── app/                                    # Core application logic
│   ├── __init__.py                         # Makes the 'app' directory a Python package
│   ├── crud.py                             # Contains CRUD database operations
│   ├── database.py                         # Database connection setup, engine, and session management
│   ├── entities.py                         # SQLAlchemy table definitions (schema for database tables)
│   ├── llm.py                              # LLM integration with Semantic Kernel setup
│   ├── mappers.py                          # Functions for mapping between Pydantic models and SQLAlchemy entities
│   ├── models.py                           # Pydantic models for request/response validation and serialization
│   ├── plugins/                            # Semantic Kernel plugins for MCP functionality
│   │   ├── __init__.py                     # Makes plugins directory a Python package
│   │   ├── functions/                      # Individual function implementations for plugins
│   │   │   ├── __init__.py                 # Makes functions directory a Python package
│   │   │   ├── create_person_function.py   # Function to create a person via MCP
│   │   │   ├── delete_person_function.py   # Function to delete a person via MCP
│   │   │   ├── get_people_function.py      # Function to list people via MCP
│   │   │   ├── get_person_function.py      # Function to get a specific person via MCP
│   │   │   └── update_person_function.py   # Function to update a person via MCP
│   │   ├── people_crud_plugin.py           # Plugin that exposes CRUD operations to LLMs
│   │   └── system_prompt_plugin.py         # Plugin that provides system prompts for LLMs
│   └── routes/                             # API router modules
│       ├── __init__.py                     # Makes the 'routes' directory a Python package
│       ├── api.py                          # FastAPI router for people CRUD endpoints
│       ├── health.py                       # Health check endpoints
│       ├── chat.py                         # Chat endpoint
│       └── mcp.py                          # Model Context Protocol endpoints
├── main.py                                 # Main FastAPI application entry point
├── people.db                               # Default SQLite database file (Gitignored)
├── pytest.ini                              # Configuration file for pytest
├── requirements.txt                        # Lists project dependencies for pip
└── tests/                                  # Contains all automated tests for the application
    ├── __init__.py                         # Makes the 'tests' directory a Python package
    ├── conftest.py                         # Pytest fixtures and configuration shared across tests
    ├── test_crud.py                        # Unit tests for CRUD operations
    ├── test_database.py                    # Unit tests for database connection and utility functions
    └── test_mappers.py                     # Unit tests for mapping functions
```

## Directory and File Descriptions

### Root Directory

*   **README.md**: Provides essential information about the project, including setup instructions, how to run the application, and an overview of its purpose.
*   **main.py**: The entry point for the FastAPI application. It initializes the FastAPI app instance, includes the API routers, and can configure global middleware or event handlers.
*   **requirements.txt**: Specifies all Python package dependencies required to run the project. This file is used by `pip` to install the necessary libraries.
*   **pytest.ini**: Configuration file for `pytest`. Used here to set options like the default asyncio loop scope to manage warnings and ensure consistent test behavior.
*   **.venv/**: Contains the Python virtual environment specific to this project. This directory is typically gitignored and includes installed packages and Python interpreter copies, ensuring project isolation.
*   **.docs/**: Holds project-related documentation files.
    *   **ARCHITECTURE.md**: Describes the overall architecture of the application, including components and their interactions.
    *   **FUNCTIONS.md**: Provides detailed explanations of important functions within the codebase.
    *   **LEARNING.md**: A collection of notes, insights, and learnings gathered during the development process.
    *   **SOLUTION.md**: This document, providing an overview of the project structure and file descriptions.
    *   **MCP.md**: Documentation about the Model Context Protocol implemented in the project.
    *   **INTEGRATION.md**: Guide for integrating the MCP with various AI platforms like OpenAI, Azure, and Claude.
    *   **LLM.md**: Details on the LLM integration aspects of the project.
    *   **AGENTIC.md**: Explanation of the agentic microservices concept and implementation.
*   **.env**: Stores environment-specific variables, such as database connection strings, API keys, or secret keys. This file is gitignored to prevent sensitive information from being committed to version control.
*   **people.db**: The default SQLite database file used by the application when not running in test mode or when a specific `DATABASE_URL` is not provided via the `.env` file. This file is typically gitignored.

### App Directory

*   **app/__init__.py**: Makes the `app` directory a Python package.
*   **app/database.py**: Handles the database connection setup, creates engine instances, and provides session management functions.
*   **app/entities.py**: Contains SQLAlchemy table definitions for the database schema (currently just the `people` table).
*   **app/models.py**: Defines Pydantic models for API request/response validation and serialization, as well as models for MCP integrations.
*   **app/mappers.py**: Provides utility functions for mapping between Pydantic models and SQLAlchemy entities.
*   **app/crud.py**: Implements CRUD operations for the `people` table.
*   **app/llm.py**: Sets up Semantic Kernel with OpenAI integration, loads plugins, and provides functions for LLM interactions.

*   **app/routes/**: Directory containing the API router modules.
    *   **app/routes/api.py**: Implements REST API endpoints for the `/people` resource.
    *   **app/routes/health.py**: Provides health check and status endpoints.
    *   **app/routes/mcp.py**: Implements the Model Context Protocol endpoints for AI integrations.

*   **app/plugins/**: Directory containing Semantic Kernel plugins and their functions.
    *   **app/plugins/people_crud_plugin.py**: Plugin that exposes CRUD operations to LLMs via Semantic Kernel.
    *   **app/plugins/system_prompt_plugin.py**: Plugin that provides system prompts for LLM guidance.
    *   **app/plugins/functions/**: Directory with individual function implementations for the plugins.

### Tests Directory

*   **tests/__init__.py**: Makes the `tests` directory a Python package.
*   **tests/conftest.py**: Contains common pytest fixtures and configurations used across multiple test files.
*   **tests/test_crud.py**: Unit tests for the CRUD operations in `app/crud.py`.
*   **tests/test_database.py**: Unit tests for database connection and utility functions.
*   **tests/test_mappers.py**: Unit tests for mapping functions in `app/mappers.py`.

### app/ Directory

This directory contains the core logic of the application, structured into several modules:

*   **__init__.py**: An empty file that tells Python to treat the `app` directory as a package, allowing modules within it to be imported using `app.module_name`.
*   **database.py**: Handles all database-related setup. This includes defining the database URL, creating the SQLAlchemy engine, and managing database sessions. It provides functions to connect to and disconnect from the database.
*   **entities.py**: Defines the structure of database tables using SQLAlchemy's declarative base. Each class here typically represents a table in the database.
*   **models.py**: Contains Pydantic models used for data validation, serialization, and documentation. These models define the expected structure for API request bodies and response payloads.
*   **crud.py**: Implements the Create, Read, Update, and Delete (CRUD) operations for the application's data. These functions interact directly with the database via SQLAlchemy, using the models defined in `entities.py` and `models.py`.
*   **mappers.py**: Provides utility functions to map data between different Pydantic models or between Pydantic models and SQLAlchemy ORM objects (entities). This helps in decoupling the API layer from the database layer.
*   **routes.py**: (Previously `app/routers/people.py`) Defines the API endpoints using FastAPI's `APIRouter`. Each function here corresponds to an API operation (e.g., GET, POST, PUT, DELETE) and handles incoming requests, calls appropriate CRUD functions, and returns responses.

### tests/ Directory

This directory houses all the automated tests for the application, ensuring code quality and correctness:

*   **__init__.py**: An empty file that makes the `tests` directory a Python package.
*   **conftest.py**: A special pytest file used to define fixtures, hooks, and plugins that are shared across multiple test files within this directory and its subdirectories. For example, it sets up the test database session.
*   **test_crud.py**: Contains unit tests specifically for the functions defined in `app/crud.py`. These tests verify that data is correctly created, retrieved, updated, and deleted from the database.
*   **test_database.py**: Includes tests for the database connection logic and utility functions in `app/database.py`. It ensures the database can be connected to and disconnected from correctly.
*   **test_mappers.py**: Contains unit tests for the data mapping functions found in `app/mappers.py`, ensuring that data transformations between different model types are accurate.
