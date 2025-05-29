# Solution Architecture

This document outlines the architecture of the Python FastAPI microservice for managing people.

## High-Level Component Diagram

This diagram shows the main components of the application and their interactions.

```mermaid
graph LR
    Client --> FastAPI_App[FastAPI Application]
    FastAPI_App --> Database[SQLite Database]

    subgraph FastAPI_App
        Router[app.routes.py] --> CRUD[app.crud.py]
        Router --> API_Models[app.models.py]
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
*   **FastAPI Application**: The core of the service.
    *   **`app.routes.py` (Router)**: Handles incoming HTTP requests for the `/people` endpoint. It uses API Models for request validation and response serialization and delegates business logic to the CRUD layer.
    *   **`app.models.py` (API Models)**: Contains Pydantic models (`PersonCreateRequest`, `PersonUpdateRequest`, `PersonResponse`) that define the structure of API request and response bodies. Ensures data validation.
    *   **`app.crud.py` (CRUD Layer)**: Implements the core business logic for Create, Read, Update, and Delete operations on people. It uses Mappers to convert between API models and database entities.
    *   **`app.mappers.py` (Mappers)**: Provides functions to translate data between API models (from `app.models.py`) and the internal `PersonEntity` Pydantic model (from `app.entities.py`).
    *   **`app.entities.py` (Database Entities & Model)**:
        *   Defines the SQLAlchemy `people` table structure.
        *   Contains the `PersonEntity` Pydantic model, which represents a person record as used internally by the CRUD and Mapper layers after retrieval from or before insertion/update to the database.
    *   **`app.database.py` (Database Interface)**: Manages the database connection (using `databases` library) and provides functions to execute SQL queries.
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
