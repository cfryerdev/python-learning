# LLM Integration with Semantic Kernel

## Overview

This project integrates Large Language Models (LLMs) using Microsoft's Semantic Kernel framework to create an extensible and modular AI application. The integration enables AI capabilities including tool usage, contextual reasoning, and plugin-based architecture.

## Key Components

### 1. Semantic Kernel

[Semantic Kernel](https://github.com/microsoft/semantic-kernel) is an open-source SDK developed by Microsoft that provides a framework for integrating LLMs into applications. Key features include:

- **Plugin Architecture**: Enables organizing AI functionality into reusable components
- **Function Calling**: Facilitates LLM's capability to call tools when needed
- **Multi-modal Support**: Handles various types of data beyond just text
- **Memory & Context**: Manages conversation history and contextual information
- **Multi-provider Support**: Works with various AI services (OpenAI, Azure, etc.)

### 2. LLM Setup (`app/llm.py`)

The `llm.py` file centralizes our LLM configuration and serves as the main integration point between our application and AI capabilities:

```python
# Initialize OpenAI client and Semantic Kernel
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
kernel = Kernel()
kernel.add_service(
    OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id=os.getenv("OPENAI_API_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
)

# Load plugins into the kernel
kernel.add_plugin(PeopleCRUDPlugin(), plugin_name="PeopleCRUD")
kernel.add_plugin(SystemPromptPlugin(), plugin_name="SystemPrompt")
```

The file also contains utility functions:

- `get_llm_response()`: Direct method to get responses from the LLM
- `process_with_llm_tool()`: Simulates LLM tool usage (placeholder for more advanced implementations)

### 3. Plugin System

Plugins are the foundation of extensibility in our application. Each plugin is a collection of related functions that can be invoked by the LLM.

#### Plugin Structure

A plugin in our system follows this pattern:

1. **Plugin Class**: A container for related functions
2. **Kernel Functions**: Methods decorated with `@kernel_function` that the LLM can invoke
3. **Parameter Metadata**: Type hints and metadata for function parameters using `KernelParameterMetadata`

Example from `PeopleCRUDPlugin`:

```python
class PeopleCRUDPlugin:
    """Container for all people CRUD operations."""
    
    @kernel_function(
        description="Creates a new person in the system.",
        name="create_person"
    )
    async def create_person(self, person_data_json):
        """Creates a new person in the system."""
        return await self.create_plugin.create_person_from_json_async(person_data_json)
```

### 4. Available Plugins

#### PeopleCRUD Plugin

Provides Create, Read, Update, Delete operations for managing people records:

- `create_person`: Create a new person record
- `get_person_by_id`: Retrieve a specific person by ID
- `get_all_people`: List all people with pagination
- `update_person_by_id`: Update an existing person
- `delete_person_by_id`: Delete a person record

#### SystemPrompt Plugin

Provides system prompts that guide the LLM's behavior:

- `get_system_prompt`: Returns a detailed system prompt describing available tools

### 5. Function Parameters

Function parameters are defined using `KernelParameterMetadata` to provide rich information to the LLM about expected inputs:

```python
async def get_all_people(
    self,
    skip: KernelParameterMetadata(
        description="Number of records to skip for pagination. Defaults to 0 if not provided.",
        name="skip",
        is_required=False,
        default_value=0,
        type="integer"
    ),
    limit: KernelParameterMetadata(
        description="Maximum number of records to return. Defaults to 100 if not provided.",
        name="limit",
        is_required=False,
        default_value=100,
        type="integer"
    )
) -> str:
```

## Model Context Protocol (MCP) Integration

The Model Context Protocol implementation in `routes/mcp.py` provides API endpoints that enable:  

1. **Tool Discovery**: `/mcp/` endpoint to discover available plugins and functions
2. **Direct Tool Execution**: `/mcp/execute_tool` endpoint to call specific functions
3. **Chat with Tool Usage**: `/mcp/chat` endpoint for conversational interaction with tool usage

## Environment Configuration

The LLM integration uses environment variables for configuration:

- `OPENAI_API_KEY`: The OpenAI API key
- `OPENAI_API_MODEL`: The model to use (defaults to "gpt-4o-mini" if not specified)

## Extending with New Plugins

To create a new plugin:

1. Create a new plugin class
2. Decorate methods with `@kernel_function`
3. Define parameters with `KernelParameterMetadata`
4. Register the plugin with the kernel in `llm.py`
5. Update the system prompt in `SystemPromptPlugin` to inform the LLM about the new capabilities

Example of a new plugin:

```python
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class WeatherPlugin:
    """Plugin for getting weather information."""
    
    @kernel_function(
        description="Gets the current weather for a given location.",
        name="get_weather"
    )
    async def get_weather(self, location: str) -> str:
        """Gets the current weather for a given location."""
        # Implementation here
        return f"Weather information for {location}"
```

Then register in `llm.py`:

```python
from .plugins.weather_plugin import WeatherPlugin

# Add to kernel
kernel.add_plugin(WeatherPlugin(), plugin_name="Weather")
```

## Debugging and Testing

For debugging LLM interactions and tool calling:

1. Use `/mcp/` endpoint to verify plugin registration
2. Test direct function execution using `/mcp/execute_tool`
3. Monitor logs during chat sessions to observe tool selection and execution

## Best Practices

1. **Function Descriptions**: Provide clear descriptions for functions and parameters
2. **Parameter Validation**: Validate and handle inputs appropriately in plugin functions
3. **Error Handling**: Implement robust error handling in plugin functions
4. **System Prompt Design**: Craft clear system prompts that effectively guide the LLM
5. **Testing**: Test plugins both directly and via the LLM's tool-calling capability