# app/routes/mcp.py
import os
import json
from fastapi import APIRouter, status, HTTPException

from openai import OpenAI

from semantic_kernel.functions.kernel_arguments import KernelArguments

from ..llm import kernel
from ..models import ChatRequest

## ====================================================

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={404: {"description": "Not found"}},
)

## ====================================================

@router.post("/chat", summary="Chat with LLM using Semantic Kernel and tools")
async def chat(request: ChatRequest):
    try:
        # 1. Get system message from the SystemPrompt plugin if available
        try:
            if "SystemPrompt" in kernel.plugins and "get_system_prompt" in kernel.plugins["SystemPrompt"]:
                system_prompt_function = kernel.plugins["SystemPrompt"]["get_system_prompt"]
                system_prompt_result = await kernel.invoke(system_prompt_function)
                # Check if the result has a value attribute
                if hasattr(system_prompt_result, 'value'):
                    # Check if the value is a dict with 'system_prompt' key
                    if isinstance(system_prompt_result.value, dict) and 'system_prompt' in system_prompt_result.value:
                        system_message = system_prompt_result.value['system_prompt']
                    else:
                        system_message = str(system_prompt_result.value)
                else:
                    system_message = str(system_prompt_result)
            else:
                system_message = "You are a helpful assistant with access to tools. Analyze the user's question and use the appropriate tools when needed to get information."
        except Exception as e:
            print(f"Error getting system prompt: {e}")
            system_message = "You are a helpful assistant with access to tools. Analyze the user's question and use the appropriate tools when needed to get information."

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
            
            # Handle parameters properly
            for param in func_metadata.parameters:
                # Set default type to string if not specified
                param_type = "string"
                
                # Add the parameter with proper type and description
                parameters["properties"][param.name] = {
                    "type": param_type,
                    "description": param.description or f"Parameter {param.name}"
                }
            
            # Create the tool definition with proper schema
            tools.append({
                "type": "function",
                "function": {
                    "name": f"{plugin.name}_{func_name}",
                    "description": func_metadata.description or f"Function to {func_name}",
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
                    
                    # Process arguments to ensure correct types
                    processed_args = {}
                    for param_name, param_value in function_args.items():
                        # For now, we'll just ensure strings are strings and handle nulls
                        if param_value is None:
                            processed_args[param_name] = ""
                        else:
                            processed_args[param_name] = str(param_value)
                    
                    # Convert processed arguments to KernelArguments
                    kernel_args = KernelArguments(**processed_args)
                    
                    # Call the function
                    try:
                        result = await kernel.invoke(kernel_function, arguments=kernel_args)
                        if hasattr(result, 'value'):
                            if result.value is None:
                                tool_result = "Operation completed successfully."
                            else:
                                tool_result = str(result.value)
                        else:
                            tool_result = str(result)
                    except Exception as e:
                        print(f"Error executing {plugin_name}.{func_name}: {str(e)}")
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
