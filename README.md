# People API

A simple microservice API to manage a list of people, built with Python, FastAPI, and SQLite.

## Documentation

- [New to Python](./.docs/LEARNING.md)
- [The Solution](./.docs/SOLUTION.md)
- [Architecture Details](./.docs/ARCHITECTURE.md)

## Features

- CRUD operations for people (Create, Read, Update, Delete)
- Swagger UI for API documentation and testing
- SQLite database for persistence
- Configuration via `.env` file

## Setup and Run

1.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

    The API will be available at `http://127.0.0.1:8000` and the Swagger UI at `http://127.0.0.1:8000/docs`.

## Running the unit tests

You can run the unit tests with the following command:

```bash
python -m pytest -v
```
Or by using pytest directly:

```bash
pytest -v
```
