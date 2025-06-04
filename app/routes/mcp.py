# app/routes/mcp.py
from typing import Any # Added
from fastapi import APIRouter, status, HTTPException

from openai import OpenAI
import os
import json
from typing import List, Dict, Any

from semantic_kernel.contents import ChatHistory, ChatMessageContent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.functions.kernel_arguments import KernelArguments

from ..llm import kernel
from ..models import ChatRequest, ExecuteToolRequest

## ====================================================

router = APIRouter(
    prefix="/mcp",
    tags=["MCP"],
    responses={404: {"description": "Not found"}},
)

## ====================================================

@router.get("/", response_model=dict, status_code=status.HTTP_200_OK, summary="MCP Availability and Plugin Details")
async def mcp_availability():
    """
    Returns a detailed list of available plugins, their functions, and descriptions.
    """
    plugins_details = []
    if kernel.plugins:
        for plugin_name, plugin in kernel.plugins.items():
            functions_details = []
            for func_name, func_metadata in plugin.functions.items():
                functions_details.append({
                    "name": func_name,
                    "description": func_metadata.description,
                    "parameters": [p.name for p in func_metadata.parameters]
                })
            
            plugins_details.append({
                "name": plugin_name,
                "functions": functions_details
            })
            
    return {"status": "MCP is available", "plugins": plugins_details}

## ====================================================

@router.post("/execute_tool", response_model=Any, status_code=status.HTTP_200_OK, summary="Execute a specific tool function") # Changed response_model to Any
async def execute_tool(request: ExecuteToolRequest):
    """
    Executes a specific function from a Semantic Kernel plugin.

    - **plugin_name**: The name of the plugin.
    - **function_name**: The name of the function within the plugin.
    - **arguments**: A dictionary of arguments to pass to the function.
    - **Returns**: The direct result of the executed plugin function.
    """
    try:
        if not kernel.plugins:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Kernel plugins not loaded.")

        if request.plugin_name not in kernel.plugins:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Plugin '{request.plugin_name}' not found. Available: {list(kernel.plugins.keys())}")
        
        plugin = kernel.plugins[request.plugin_name]
        
        if request.function_name not in plugin:
            functions_in_plugin = [f.name for f in plugin.functions.values()]
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Function '{request.function_name}' not found in plugin '{request.plugin_name}'. Available functions: {functions_in_plugin}")
            
        kernel_function = plugin[request.function_name]
        
        # Prepare arguments for the kernel function
        kernel_args = KernelArguments(**request.arguments)
        
        # Invoke the kernel function
        result = await kernel.invoke(kernel_function, arguments=kernel_args)
        
        # Process the result value
        response_value = result.value
        # Plugins are expected to return JSON strings, but let's be safe
        if not isinstance(response_value, (str, int, float, bool, dict, list, type(None))):
            response_value = str(response_value)
            
        return response_value # Changed: Return the direct value
        
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        # Log the full error for debugging
        print(f"Error in /mcp/execute_tool: {type(e).__name__} - {str(e)}")
        # Optionally include traceback: import traceback; traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred while executing the tool: {str(e)}")

## ====================================================

@router.post("/chat", summary="Chat with LLM using Semantic Kernel and tools")
async def chat(request: ChatRequest):
    try:
        # 1. Get system message from the SystemPrompt plugin if available
        try:
            if "SystemPrompt" in kernel.plugins and "get_system_prompt" in kernel.plugins["SystemPrompt"]:
                system_prompt_function = kernel.plugins["SystemPrompt"]["get_system_prompt"]
                system_prompt_result = await kernel.invoke(system_prompt_function)
                system_message = str(system_prompt_result.value)
            else:
                system_message = "You are a helpful assistant that can answer questions. For this conversation, you do NOT have access to any external tools or databases. Please respond based solely on your knowledge."
        except Exception as e:
            print(f"Error getting system prompt: {e}")
            system_message = "You are a helpful assistant that can answer questions. For this conversation, you do NOT have access to any external tools or databases. Please respond based solely on your knowledge."

        # 2. Prepare the conversation history as a simple formatted string
        conversation = f"System: {system_message}\n\n"
        
        # Add previous messages from request if any
        for msg in request.chat_history:
            if msg.get("role") == "user":
                conversation += f"User: {msg.get('content', '')}\n"
            elif msg.get("role") == "assistant":
                conversation += f"Assistant: {msg.get('content', '')}\n"

        # Add the current user query
        conversation += f"User: {request.user_query}\n"
        conversation += "Assistant: "
        
        # Check if PeopleCRUD plugin is available
        tools = []
        plugin = kernel.plugins["PeopleCRUD"]
        
        # Convert plugin functions to OpenAI tool format
        for func_name, func_metadata in plugin.functions.items():
            # Extract parameters for the function
            parameters = {
                "type": "object",
                "properties": {}
            }
            
            for param in func_metadata.parameters:
                parameters["properties"][param.name] = {"type": "string", "description": param.description}
            
            # Create the tool definition
            tools.append({
                "type": "function",
                "function": {
                    "name": f"{plugin.name}_{func_name}",
                    "description": func_metadata.description,
                    "parameters": parameters
                }
            })
        
        # Make the API call with tools configuration
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        openai_response = client.chat.completions.create(
            model=os.getenv("OPENAI_API_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_message},
                *[{"role": msg.get("role"), "content": msg.get("content", "")} for msg in request.chat_history],
                {"role": "user", "content": request.user_query}
            ],
            tools=tools,
            tool_choice="auto"
        )
        
        # Handle the response, potentially including tool calls
        assistant_message = openai_response.choices[0].message
        
        # Check if the model wants to call a tool
        if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
            # The model wants to use a tool
            tool_results = []
            
            # Process each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Extract plugin_name and actual function name
                if "_" in function_name:
                    plugin_name, func_name = function_name.split("_", 1)
                else:
                    # Handle case where naming is different
                    plugin_name = "PeopleCRUD"  # Default plugin
                    func_name = function_name
                
                print(f"Tool call: {plugin_name}.{func_name} with args: {function_args}")
                
                # Execute the function using the kernel
                if plugin_name in kernel.plugins and func_name in kernel.plugins[plugin_name]:
                    # Get the function from the plugin
                    kernel_function = kernel.plugins[plugin_name][func_name]
                    
                    # Convert arguments to KernelArguments
                    kernel_args = KernelArguments(**function_args)
                    
                    # Call the function
                    try:
                        result = await kernel.invoke(kernel_function, arguments=kernel_args)
                        if hasattr(result, 'value'):
                            tool_result = str(result.value)
                        else:
                            tool_result = str(result)
                    except Exception as e:
                        tool_result = f"Error executing function: {str(e)}"
                else:
                    tool_result = f"Function {plugin_name}.{func_name} not found"
                
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": tool_result
                })
            
            # Create messages for further processing with the tool results
            tool_messages = [
                {"role": "system", "content": system_message},
                *[{"role": msg.get("role"), "content": msg.get("content", "")} for msg in request.chat_history],
                {"role": "user", "content": request.user_query},
                assistant_message.model_dump(),  # Include the assistant's tool call message
                *[{"role": "tool", "tool_call_id": result["tool_call_id"], "name": result["name"], "content": result["content"]} for result in tool_results]
            ]
            
            # Send the tool results back to the model for a final response
            final_response = client.chat.completions.create(
                model=os.getenv("OPENAI_API_MODEL", "gpt-4o-mini"),
                messages=tool_messages
            )
            
            # Get the final response after tool usage
            llm_response_content = final_response.choices[0].message.content or ""
            
            # Create complete chat history including tool usage
            tool_usage_summary = "\n\n[Used tools: " + ", ".join([result["name"] for result in tool_results]) + "]"
            current_turn_history = request.chat_history + [
                {"role": "user", "content": request.user_query},
                {"role": "assistant", "content": llm_response_content + tool_usage_summary}
            ]
        else:
            # No tool calls, just get the text response
            llm_response_content = assistant_message.content or ""
            
            # Create response history for continuity
            current_turn_history = request.chat_history + [
                {"role": "user", "content": request.user_query},
                {"role": "assistant", "content": llm_response_content}
            ]
        
        # We've already set llm_response_content and current_turn_history above
        return {"llm_response": llm_response_content.strip(), "chat_history": current_turn_history}

    except Exception as e:
        print(f"Error in /mcp/chat: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
