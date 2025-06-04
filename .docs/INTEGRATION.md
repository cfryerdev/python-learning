# Integrating MCP with AI Platforms

This document provides guidance on integrating the Model Context Protocol (MCP) with various AI platforms, enabling them to leverage the tools and functionalities exposed by this application.

## Table of Contents

- [OpenAI Integration](#openai-integration)
- [Claude Desktop Integration](#claude-desktop-integration)
- [Azure AI Function Calling](#azure-ai-function-calling)

## OpenAI Integration

OpenAI models support function calling, which allows the model to generate structured output that can invoke functions defined in your application.

### Setup

1. Install the OpenAI Python package:
   ```bash
   pip install openai
   ```

2. Set up your API key:
   ```python
   from openai import OpenAI
   
   client = OpenAI(api_key="your-api-key")
   ```

3. Prepare function definitions that map to your MCP plugins:
   ```python
   functions = [
     {
       "name": "create_person",
       "description": "Creates a new person in the system",
       "parameters": {
         "type": "object",
         "properties": {
           "person_data_json": {
             "type": "string",
             "description": "JSON string with required fields 'first_name', 'last_name' and optional fields 'age', 'email'."
           }
         },
         "required": ["person_data_json"]
       }
     }
     # Add other functions here
   ]
   ```

4. Call the OpenAI API with function definitions:
   ```python
   response = client.chat.completions.create(
     model="gpt-4", 
     messages=[{"role": "user", "content": user_query}],
     functions=functions,
     function_call="auto"
   )
   ```

5. Process the response to execute the MCP function if needed:
   ```python
   message = response.choices[0].message
   if message.function_call:
       function_name = message.function_call.name
       function_args = json.loads(message.function_call.arguments)
       
       # Call your MCP endpoint
       mcp_payload = {
           "plugin_name": "PeopleCRUD",  # Determine the plugin name based on function_name
           "function_name": function_name,
           "arguments": function_args
       }
       mcp_response = requests.post("http://your-api-url/mcp/execute_tool", json=mcp_payload).json()
       
       # Send the result back to OpenAI
       final_response = client.chat.completions.create(
           model="gpt-4",
           messages=[
               {"role": "user", "content": user_query},
               message,
               {"role": "function", "name": function_name, "content": json.dumps(mcp_response)}
           ]
       )
       return final_response.choices[0].message.content
   else:
       return message.content
   ```

## Claude Desktop Integration

The Claude Desktop application supports tool use through a developer settings configuration. You can integrate your MCP with Claude Desktop by adding a JSON configuration that defines your tools.

### JSON Configuration for Claude Desktop

To add your MCP tools to Claude Desktop:

1. Open Claude Desktop and access the developer settings
2. Add a new tool configuration by pasting the following JSON payload:

```json
{
  "schema_version": "v1",
  "name_for_human": "People API MCP",
  "name_for_model": "PeopleCRUD",
  "description_for_human": "Allows you to create, read, update, and delete people records in the system.",
  "description_for_model": "This plugin provides CRUD operations for managing people records in the database.",
  "auth": {
    "type": "none"
  },
  "api": {
    "type": "openapi",
    "url": "http://localhost:8000/mcp/",
    "has_user_authentication": false
  },
  "endpoints": [
    {
      "name": "create_person",
      "description": "Creates a new person in the system",
      "endpoint": "/mcp/execute_tool",
      "method": "POST",
      "request_body": {
        "plugin_name": "PeopleCRUD",
        "function_name": "create_person",
        "arguments": {
          "person_data_json": "$person_data_json"
        }
      },
      "input_schema": {
        "type": "object",
        "properties": {
          "person_data_json": {
            "type": "string",
            "description": "JSON string with required fields 'first_name', 'last_name' and optional fields 'age', 'email'."
          }
        },
        "required": ["person_data_json"]
      }
    },
    {
      "name": "get_person_by_id",
      "description": "Retrieves a specific person by their unique ID",
      "endpoint": "/mcp/execute_tool",
      "method": "POST",
      "request_body": {
        "plugin_name": "PeopleCRUD",
        "function_name": "get_person_by_id",
        "arguments": {
          "person_id": "$person_id"
        }
      },
      "input_schema": {
        "type": "object",
        "properties": {
          "person_id": {
            "type": "integer",
            "description": "Integer ID of the person to retrieve."
          }
        },
        "required": ["person_id"]
      }
    },
    {
      "name": "get_all_people",
      "description": "Retrieves a list of all people with pagination support",
      "endpoint": "/mcp/execute_tool",
      "method": "POST",
      "request_body": {
        "plugin_name": "PeopleCRUD",
        "function_name": "get_all_people",
        "arguments": {
          "skip": "$skip",
          "limit": "$limit"
        }
      },
      "input_schema": {
        "type": "object",
        "properties": {
          "skip": {
            "type": "integer",
            "description": "Number of records to skip (default: 0)."
          },
          "limit": {
            "type": "integer",
            "description": "Maximum number of records to return (default: 100)."
          }
        }
      }
    },
    {
      "name": "update_person_by_id",
      "description": "Updates an existing person by their unique ID",
      "endpoint": "/mcp/execute_tool",
      "method": "POST",
      "request_body": {
        "plugin_name": "PeopleCRUD",
        "function_name": "update_person_by_id",
        "arguments": {
          "person_id": "$person_id",
          "person_update_data_json": "$person_update_data_json"
        }
      },
      "input_schema": {
        "type": "object",
        "properties": {
          "person_id": {
            "type": "integer",
            "description": "Integer ID of the person to update."
          },
          "person_update_data_json": {
            "type": "string",
            "description": "JSON string with fields to update ('first_name', 'last_name', 'age', 'email')."
          }
        },
        "required": ["person_id", "person_update_data_json"]
      }
    },
    {
      "name": "delete_person_by_id",
      "description": "Deletes a person by their unique ID",
      "endpoint": "/mcp/execute_tool",
      "method": "POST",
      "request_body": {
        "plugin_name": "PeopleCRUD",
        "function_name": "delete_person_by_id",
        "arguments": {
          "person_id": "$person_id"
        }
      },
      "input_schema": {
        "type": "object",
        "properties": {
          "person_id": {
            "type": "integer",
            "description": "Integer ID of the person to delete."
          }
        },
        "required": ["person_id"]
      }
    }
  ]
}
```

### Usage Notes

1. Update the `url` field in the JSON configuration to point to where your MCP API is hosted (default is `http://localhost:8000/mcp/`)

2. Make sure your MCP API server is running before attempting to use the tools in Claude Desktop

3. The configuration automatically maps Claude's tool calls to your MCP's execute_tool endpoint, with the appropriate plugin and function names for each operation

4. If you need to add authentication, update the "auth" section of the configuration with the appropriate authentication type and credentials

## Azure AI Function Calling

Azure OpenAI Service supports function calling similar to OpenAI, with the added benefits of Azure's security, compliance, and regional availability.

### Setup

1. Install the Azure OpenAI package:
   ```bash
   pip install azure-openai
   ```

2. Configure your Azure OpenAI client:
   ```python
   from azure.openai import AzureOpenAI
   
   client = AzureOpenAI(
     api_key="your-azure-api-key",
     api_version="2023-12-01-preview",
     azure_endpoint="https://your-resource-name.openai.azure.com"
   )
   ```

3. Define functions that map to your MCP plugins:
   ```python
   functions = [
     {
       "name": "create_person",
       "description": "Creates a new person in the system",
       "parameters": {
         "type": "object",
         "properties": {
           "person_data_json": {
             "type": "string",
             "description": "JSON string with required fields 'first_name', 'last_name' and optional fields 'age', 'email'."
           }
         },
         "required": ["person_data_json"]
       }
     }
     # Add other functions here
   ]
   ```

4. Call the Azure OpenAI API with function definitions:
   ```python
   response = client.chat.completions.create(
     model="your-deployed-model",  # The name of your deployed model
     messages=[{"role": "user", "content": user_query}],
     functions=functions,
     function_call="auto"
   )
   ```

5. Process the response to execute the MCP function if needed:
   ```python
   message = response.choices[0].message
   if message.function_call:
     function_name = message.function_call.name
     function_args = json.loads(message.function_call.arguments)
     
     # Call your MCP endpoint
     mcp_payload = {
       "plugin_name": "PeopleCRUD",  # Determine the plugin name based on function_name
       "function_name": function_name,
       "arguments": function_args
     }
     mcp_response = requests.post("http://your-api-url/mcp/execute_tool", json=mcp_payload).json()
     
     # Send the result back to Azure OpenAI
     final_response = client.chat.completions.create(
       model="your-deployed-model",
       messages=[
         {"role": "user", "content": user_query},
         message,
         {"role": "function", "name": function_name, "content": json.dumps(mcp_response)}
       ]
     )
     return final_response.choices[0].message.content
   else:
     return message.content
   ```

### Azure AI Integration Best Practices

1. **Resource Management**: Use Azure Resource Manager to provision and manage your OpenAI resources in a consistent way.

2. **Security**: Utilize Azure Key Vault for securely storing API keys and other sensitive credentials.

3. **Network Security**: Configure your Azure OpenAI resources with private endpoints for enhanced security.

4. **Monitoring**: Implement Azure Monitor to track the usage, performance, and costs of your Azure OpenAI resources.

5. **Compliance**: Take advantage of Azure's compliance certifications when working with sensitive data.

6. **Rate Limiting**: Implement appropriate rate limiting strategies to manage costs and ensure service availability.