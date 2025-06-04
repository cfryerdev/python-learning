# Solution Architecture

This document outlines the architecture of the Python FastAPI microservice for managing people, including the LLM integration via Model Context Protocol (MCP).

## High-Level Component Diagram

This diagram shows the main components of the application and their interactions.

```mermaid
graph LR
    Client --> Router[app.routes.api]
    LLM_Client[LLM Client] --> MCP_Endpoints[app.routes.mcp]
    FastAPI_App[FastAPI Application] --> Database[SQLite Database]

    subgraph FastAPI_App
        Router --> CRUD[app.crud.py]
        Router --> API_Models[app.models.py]
        MCP_Endpoints --> LLM_Kernel[app.llm.py]
        LLM_Kernel --> Plugins[app.plugins]
        Plugins --> CRUD
        CRUD --> Mappers[app.mappers.py]
        CRUD --> DB_Entities_Model[app.entities.py PersonEntity Pydantic Model]
        Mappers --> API_Models
        Mappers --> DB_Entities_Model
        CRUD --> DB_Interface[app.database.py & app.entities.py SQLAlchemy Table]
    end

    DB_Interface --> Database
```

**Components:**

*   **Client**: Any HTTP client (e.g., browser, mobile app, another service) that consumes the API.
*   **LLM_Client**: An AI language model client (e.g., OpenAI, Claude, Azure OpenAI) that interacts with the API via the MCP endpoints.
*   **FastAPI Application**: The core of the service.
    *   **`app.routes/api.py` (Router)**: Handles incoming HTTP requests for the `/people` endpoint. It uses API Models for request validation and response serialization and delegates business logic to the CRUD layer.
    *   **`app.routes/mcp.py` (MCP Router)**: Implements the Model Context Protocol endpoints that allow LLMs to interact with the application's functionality.
    *   **`app.models.py` (API Models)**: Contains Pydantic models (`PersonCreateRequest`, `PersonUpdateRequest`, `PersonResponse`) that define the structure of API request and response bodies, as well as models for MCP requests and responses.
    *   **`app.crud.py` (CRUD Layer)**: Implements the core business logic for Create, Read, Update, and Delete operations on people. It uses Mappers to convert between API models and database entities.
    *   **`app.mappers.py` (Mappers)**: Provides functions to translate data between API models (from `app.models.py`) and the internal `PersonEntity` Pydantic model (from `app.entities.py`).
    *   **`app.entities.py` (Database Entities & Model)**:
        *   Defines the SQLAlchemy `people` table structure.
        *   Contains the `PersonEntity` Pydantic model, which represents a person record as used internally by the CRUD and Mapper layers.
    *   **`app.database.py` (Database Interface)**: Manages the database connection and provides functions to execute SQL queries.
    *   **`app.llm.py` (LLM Integration)**: Sets up the Semantic Kernel integration with OpenAI and configures the LLM plugins.
    *   **`app.plugins/` (Semantic Kernel Plugins)**: Contains plugins that expose application functionality to LLMs.
        *   **`people_crud_plugin.py`**: Plugin that wraps CRUD operations for LLM access.
        *   **`system_prompt_plugin.py`**: Plugin that provides system prompts to guide LLM behavior.
        *   **`functions/`**: Directory containing individual function implementations for each plugin.
*   **SQLite Database**: The relational database used to store person data.

## Sequence Diagram: Create Person

This diagram shows the sequence of interactions when a client creates a new person.

```mermaid
sequenceDiagram
    participant Client
    participant Router as app.routes.py
    participant API_Models as app.models.PersonCreateRequest
    participant CRUD as app.crud.py
    participant Mappers as app.mappers.py
    participant DB_Entity_Model as app.entities.PersonEntity
    participant Database as SQLite (via app.database.py & entities.people table)

    Client->>+Router: POST /people (payload: PersonCreateRequest)
    Router->>+API_Models: Validate request payload
    API_Models-->>-Router: Validated person_data
    Router->>+CRUD: create_person(person_data)
    CRUD->>+Database: INSERT INTO people (values from person_data)
    Database-->>-CRUD: last_record_id
    CRUD->>+Database: SELECT * FROM people WHERE id = last_record_id (via _get_person_entity)
    Database-->>-CRUD: db_row
    CRUD->>+Mappers: to_person_entity_from_dict(db_row)
    Mappers-->>-CRUD: created_person_entity: PersonEntity
    CRUD->>+Mappers: to_person_response_from_entity(created_person_entity)
    Mappers-->>-CRUD: person_response: PersonResponse
    CRUD-->>-Router: return person_response
    Router-->>-Client: HTTP 201 Created (body: PersonResponse)
```

## Sequence Diagram: MCP Tool Execution

This diagram shows the sequence of interactions when an LLM client uses the MCP to execute a tool function (e.g., creating a person).

```mermaid
sequenceDiagram
    participant LLM_Client as LLM Client
    participant MCP_Router as app.routes.mcp.py
    participant ExecuteToolRequest as app.models.ExecuteToolRequest
    participant LLM_Kernel as app.llm.py
    participant Plugin as app.plugins.people_crud_plugin
    participant PluginFunction as app.plugins.functions.create_person_function
    participant CRUD as app.crud.py
    participant Database as SQLite Database

    LLM_Client->>+MCP_Router: POST /mcp/execute_tool (payload: {plugin_name, function_name, arguments})
    MCP_Router->>+ExecuteToolRequest: Validate request payload
    ExecuteToolRequest-->>-MCP_Router: Validated tool request
    MCP_Router->>+LLM_Kernel: Access kernel.plugins[plugin_name][function_name]
    LLM_Kernel-->>-MCP_Router: Return kernel function reference
    MCP_Router->>+Plugin: Invoke kernel function with arguments
    Plugin->>+PluginFunction: Call function implementation
    PluginFunction->>+CRUD: create_person(person_data)
    CRUD->>+Database: INSERT person data
    Database-->>-CRUD: Return created person ID
    CRUD-->>-PluginFunction: Return person response
    PluginFunction-->>-Plugin: Format result for LLM
    Plugin-->>-MCP_Router: Return function result
    MCP_Router-->>-LLM_Client: HTTP 200 OK (body: function result) 
```

## Sequence Diagram: MCP Chat Interaction

This diagram shows the sequence of interactions when a user interacts with the API via the MCP chat endpoint, allowing the LLM to decide which tools to use.

```mermaid
sequenceDiagram
    participant Client
    participant MCP_Router as app.routes.mcp.py
    participant ChatRequest as app.models.ChatRequest
    participant OpenAI_Client as OpenAI API
    participant LLM_Kernel as app.llm.py
    participant SystemPrompt as app.plugins.system_prompt_plugin
    participant PeopleCRUD as app.plugins.people_crud_plugin
    participant Database as SQLite Database

    Client->>+MCP_Router: POST /mcp/chat (payload: {user_query, chat_history})
    MCP_Router->>+ChatRequest: Validate request payload
    ChatRequest-->>-MCP_Router: Validated chat request
    MCP_Router->>+SystemPrompt: Get system prompt
    SystemPrompt-->>-MCP_Router: Return system prompt text
    MCP_Router->>+OpenAI_Client: Create completion with system prompt, user query, and available tools
    OpenAI_Client-->>-MCP_Router: Return completion with potential tool calls
    alt LLM decides to use tools
        MCP_Router->>+LLM_Kernel: Execute tool call with arguments
        LLM_Kernel->>+PeopleCRUD: Call appropriate function
        PeopleCRUD->>+Database: Perform database operation
        Database-->>-PeopleCRUD: Return data
        PeopleCRUD-->>-LLM_Kernel: Return function result
        LLM_Kernel-->>-MCP_Router: Return tool execution result
        MCP_Router->>+OpenAI_Client: Send follow-up with tool results
        OpenAI_Client-->>-MCP_Router: Return final response incorporating tool results
    end
    MCP_Router-->>-Client: HTTP 200 OK (body: {llm_response, chat_history})
```
