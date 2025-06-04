# app/routes/mcp.py
from fastapi import APIRouter, status, HTTPException

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
                    "name": func_metadata.name,
                    "description": func_metadata.description,
                    # You could also add parameters here if needed:
                    # "parameters": [p.name for p in func_metadata.parameters]
                })
            plugins_details.append({
                "name": plugin_name,
                "functions": functions_details
            })
            
    return {"status": "MCP is available", "plugins": plugins_details}

## ====================================================

@router.post("/execute_tool", response_model=dict, status_code=status.HTTP_200_OK, summary="Execute a specific tool function")
async def execute_tool(request: ExecuteToolRequest):
    """
    Executes a specific function from a Semantic Kernel plugin.

    - **plugin_name**: The name of the plugin.
    - **function_name**: The name of the function within the plugin.
    - **arguments**: A dictionary of arguments to pass to the function.
    - **Returns**: A JSON object with the plugin name, function name, and the result of the execution.
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
            
        return {
            "plugin_name": request.plugin_name, 
            "function_name": request.function_name, 
            "result": response_value
        }
        
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
        # 1. Get the system prompt from the SystemGuide plugin
        system_prompt_function = kernel.plugins["SystemGuide"]["get_system_prompt"]
        system_prompt_result = await kernel.invoke(system_prompt_function)
        system_message = str(system_prompt_result.value)

        # 2. Initialize Chat History
        chat_history = ChatHistory(system_message=system_message)
        
        # Add previous messages from request if any (for multi-turn conversations)
        for msg in request.chat_history:
            if msg.get("role") == "user":
                chat_history.add_user_message(msg.get("content", ""))
            elif msg.get("role") == "assistant":
                # Here, if assistant messages contained tool calls, they'd need special handling
                # For simplicity, we'll assume assistant messages are simple text for now.
                # Proper handling of tool_calls in history is more complex.
                chat_history.add_assistant_message(msg.get("content", ""))

        chat_history.add_user_message(request.user_query)

        # 3. Configure Prompt Execution Settings for tool calling
        # This tells the kernel to enable all functions in the 'PeopleCRUD' plugin for the LLM to use.
        execution_settings = OpenAIChatPromptExecutionSettings(
            function_choice_behavior=FunctionChoiceBehavior.Auto() # Updated to new API, allows LLM to choose from available functions,
            # service_id="chat-gpt" # Ensure this matches the service_id in llm.py if multiple services are present
        )

        # 4. Invoke the chat completion service
        # The kernel will manage the conversation flow, including calling tools if the LLM decides to.
        kernel_args = KernelArguments(settings=execution_settings)
        # For some connectors or specific setups, you might also need to pass the chat_history as an argument:
        # kernel_args["chat_history"] = chat_history # Or another appropriate key

        # 4. Invoke the chat completion service
        # The kernel will manage the conversation flow, including calling tools if the LLM decides to.
        response = await kernel.invoke(
            prompt=chat_history, # The primary prompt input
            arguments=kernel_args
        )
        
        # The response object might be complex if it includes tool calls.
        # For a simple text response from the LLM (after any tool use):
        llm_response_content = ""
        if response and response.value:
            # The primary response content is usually in response.value
            # If it's a list of ChatMessageContent, iterate and concatenate
            if isinstance(response.value, list):
                for item in response.value:
                    if isinstance(item, ChatMessageContent) and item.content:
                        llm_response_content += str(item.content) + "\n"
            elif isinstance(response.value, ChatMessageContent) and response.value.content:
                llm_response_content = str(response.value.content)
            else:
                llm_response_content = str(response.value) # Fallback
        else:
            llm_response_content = "Sorry, I couldn't process that request."

        # Prepare chat history for the response to allow continuation
        current_turn_history = []
        for msg_content in chat_history:
            current_turn_history.append({"role": str(msg_content.role.value), "content": str(msg_content.content)})
        # Add the LLM's final response to the history to be returned
        current_turn_history.append({"role": "assistant", "content": llm_response_content.strip()})

        return {"llm_response": llm_response_content.strip(), "chat_history": current_turn_history}

    except Exception as e:
        print(f"Error in /mcp/chat: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")
