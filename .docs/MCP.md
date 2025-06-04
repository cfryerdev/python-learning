# Model Context Protocol (MCP) Documentation

## What is MCP?

The Model Context Protocol (MCP) is a standardized interface for AI language models to interact with external tools, data sources, and services. In the context of AI applications, MCP enables:

1. **Tool Usage**: Allowing language models to call external functions when needed to complete tasks.
2. **Contextual Understanding**: Providing AI models with additional context beyond their training data.
3. **Standardized Communication**: Establishing a consistent protocol for AI systems to communicate with external services.
4. **Plugin Architecture**: Supporting an extensible design where new capabilities can be added as plugins.

This implementation uses Semantic Kernel's plugin architecture to expose functionality to large language models (LLMs), enabling them to perform actions like creating, retrieving, updating, and deleting people records through a well-defined API.

## API Endpoints

The MCP API provides three main endpoints:

### 1. `/mcp/`

- **Method**: GET
- **Description**: Returns information about available plugins and their functions.
- **Purpose**: This endpoint can be used to discover the available plugins and their functions through a marketplace or orchestration.
- **Response**: JSON object containing plugin names, functions, descriptions, and parameters.
- **Example Response**:
  ```json
  {
    "status": "MCP is available",
    "plugins": [
      {
        "name": "PeopleCRUD",
        "functions": [
          {
            "name": "create_person",
            "description": "Creates a new person in the system.",
            "parameters": ["person_data_json"]
          },
          ...
        ]
      },
      {
        "name": "SystemPrompt",
        "functions": [
          {
            "name": "get_system_prompt",
            "description": "Provides a system prompt that informs the LLM about available tools and their usage.",
            "parameters": []
          }
        ]
      }
    ]
  }
  ```

### 2. `/mcp/execute_tool`

- **Method**: POST
- **Description**: Executes a specific function from a Semantic Kernel plugin.
- **Purpose**: This endpoint will be used by the LLM to call specific functions from plugins.
- **Request Body**: JSON object with `plugin_name`, `function_name`, and `arguments`.
- **Response**: JSON object with the result of the function execution.

### 3. `/mcp/chat`

- **Method**: POST
- **Description**: Interacts with the LLM using available tools.
- **Purpose**: This endpoint is a testing endpoint for users to test plugins with.
- **Request Body**: JSON object with `user_query` (the user's message) and optionally `chat_history` (previous messages).
- **Response**: JSON object with the LLM's response and updated chat history.

## Available Plugins and Functions

### 1. PeopleCRUD Plugin

Provides CRUD operations for managing people records.

#### Functions:

1. `create_person`
   - **Description**: Creates a new person in the system.
   - **Parameters**: 
     - `person_data_json`: JSON string with required fields 'first_name', 'last_name' and optional fields 'age', 'email'.
   - **Returns**: Details of the created person.

2. `get_person_by_id`
   - **Description**: Retrieves a specific person by their unique ID.
   - **Parameters**: 
     - `person_id`: Integer ID of the person to retrieve.
   - **Returns**: Person details if found.

3. `get_all_people`
   - **Description**: Retrieves a list of all people with pagination support.
   - **Parameters**: 
     - `skip`: Number of records to skip (default: 0).
     - `limit`: Maximum number of records to return (default: 100).
   - **Returns**: List of people.

4. `update_person_by_id`
   - **Description**: Updates an existing person by their unique ID.
   - **Parameters**: 
     - `person_id`: Integer ID of the person to update.
     - `person_update_data_json`: JSON string with fields to update ('first_name', 'last_name', 'age', 'email').
   - **Returns**: Updated person details.

5. `delete_person_by_id`
   - **Description**: Deletes a person by their unique ID.
   - **Parameters**: 
     - `person_id`: Integer ID of the person to delete.
   - **Returns**: Confirmation message.

### 2. SystemPrompt Plugin

Provides system prompts for the LLM.

#### Functions:

1. `get_system_prompt`
   - **Description**: Returns a system prompt string that informs the LLM about available tools and their usage.
   - **Parameters**: None
   - **Returns**: Detailed system prompt text.

## Example Payloads

Here are helpful payloads you can use with the `/mcp/execute_tool` endpoint:

**Getting the system prompt**
```json
{
  "plugin_name": "SystemPrompt",
  "function_name": "get_system_prompt"
}
```

**Creating a new person**
```json
{
  "plugin_name": "PeopleCRUD",
  "function_name": "create_person",
  "arguments": { 
    "person_data_json": "{\"first_name\": \"John\", \"last_name\": \"Doe\", \"age\": 30, \"email\": \"john.doe@example.com\"}"
  }
}
```

**Getting a specific person by ID**
```json
{
  "plugin_name": "PeopleCRUD",
  "function_name": "get_person_by_id",
  "arguments": { "person_id": 1 }
}
```

**Getting all people**
```json
{
  "plugin_name": "PeopleCRUD",
  "function_name": "get_all_people"
}
```

**Getting all people with pagination**
```json
{
  "plugin_name": "PeopleCRUD",
  "function_name": "get_all_people",
  "arguments": { "skip": 0, "limit": 10 }
}
```

**Updating a person**
```json
{
  "plugin_name": "PeopleCRUD",
  "function_name": "update_person_by_id",
  "arguments": { 
    "person_id": 1,
    "person_update_data_json": "{\"first_name\": \"Jane\", \"age\": 31}"
  }
}
```

**Deleting a person**
```json
{
  "plugin_name": "PeopleCRUD",
  "function_name": "delete_person_by_id",
  "arguments": { "person_id": 1 }
}
```

## Usage with Chat

The `/mcp/chat` endpoint enables interactive conversations where the LLM can dynamically choose to use tools when appropriate. Example request:

```json
{
  "user_query": "Please add a new person named Alice Smith who is 28 years old",
  "chat_history": [
    {"role": "user", "content": "Hi, I need to manage some people records"},
    {"role": "assistant", "content": "I can help you manage people records. What would you like to do?"}
  ]
}
```

## Extending MCP with New Plugins

To add new plugins to this MCP implementation:

1. Create a new plugin class with methods decorated with `@kernel_function`
2. Add detailed descriptions for each function using the decorator parameters
3. Define parameter metadata using `KernelParameterMetadata`
4. Register your plugin with the kernel in `app/llm.py`
5. Update the system prompt in `SystemPromptPlugin` to describe the new functionality
