# app/routes/mcp.py
from typing import Dict, Optional
from fastapi import APIRouter, status, HTTPException, Response
from pydantic import BaseModel, Field

from semantic_kernel.functions.kernel_arguments import KernelArguments

from ..llm import kernel
from ..models import ExecuteToolRequest, MCPInitializeRequest, MCPToolCallRequest, MCPToolsListRequest

## ====================================================

router = APIRouter(
    prefix="/mcp",
    tags=["MCP"],
    responses={404: {"description": "Not found"}},
)

## ====================================================

@router.post("/initialize", summary="Initialize the MCP API connection")
async def initialize(request: MCPInitializeRequest):
    """
    Initialize the MCP connection with client information and protocol version.
    This endpoint is typically called first by MCP clients.
    """
    # Log client information
    client_name = request.params.clientInfo.name
    client_version = request.params.clientInfo.version

    protocolVersion = "2024-11-05"
    
    print(f"[MCP] MCP initialized with: {client_name} {client_version}, protocol version {protocolVersion}")
    
    return {
        "jsonrpc": "2.0",
        "id": request.id,
        "result": {
            "protocolVersion": protocolVersion,
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "people-api-mcp-server",
                "version": "1.0.0"
            }
        }
    }

## ====================================================

@router.post("/notifications/initialized", summary="Handle initialized notification")
async def notifications_initialized():
    """Handle the initialized notification - no response needed for notifications"""
    return Response(status_code=204)  # No Content

## ====================================================

@router.post("/notifications/cancelled", summary="Handle cancelled notification") 
async def notifications_cancelled():
    """Handle cancelled notifications - no response needed for notifications"""
    return Response(status_code=204)  # No Content

## ====================================================

@router.post("/resources/list", summary="List resources")
@router.get("/resources/list", summary="List resources")
async def resources_list(request: Optional[dict] = None):
    """Return empty resources list - this API doesn't provide resources"""
    request_id = 1
    if request and isinstance(request, dict) and 'id' in request:
        request_id = request['id']
    
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "resources": []
        }
    }

## ====================================================

@router.post("/tools/list", summary="List available MCP tools")
async def list_tools_post(request: MCPToolsListRequest):
    """Handle POST requests to tools/list with JSON-RPC format"""
    tools_list = []

    if kernel.plugins:
        for plugin_name, plugin in kernel.plugins.items():
            for func_name, func_metadata in plugin.functions.items():
                # Convert parameters to MCP inputSchema format
                properties = {}
                required_params = []
                
                for param in func_metadata.parameters:
                    properties[param.name] = {
                        "type": "string",  # Could enhance to detect actual types
                        "description": param.description or f"Parameter {param.name}"
                    }
                    if getattr(param, 'required', False):
                        required_params.append(param.name)
                
                # Add the tool in MCP format
                tools_list.append({
                    "name": func_name,
                    "description": func_metadata.description or f"Function to {func_name}",
                    "inputSchema": {
                        "type": "object",
                        "properties": properties,
                        **({"required": required_params} if required_params else {})
                    }
                })
    
    # Return in proper MCP JSON-RPC format
    return {
        "jsonrpc": "2.0",
        "id": request.id,
        "result": {
            "tools": tools_list
        }
    }

## ====================================================

@router.get("/tools/list", summary="List available MCP tools (GET)")
async def list_tools_get():
    """Handle GET requests to tools/list for backwards compatibility"""
    tools_list = []

    if kernel.plugins:
        for plugin_name, plugin in kernel.plugins.items():
            for func_name, func_metadata in plugin.functions.items():
                # Convert parameters to MCP inputSchema format
                properties = {}
                required_params = []
                
                for param in func_metadata.parameters:
                    properties[param.name] = {
                        "type": "string",
                        "description": param.description or f"Parameter {param.name}"
                    }
                    if getattr(param, 'required', False):
                        required_params.append(param.name)
                
                # Add the tool in MCP format
                tools_list.append({
                    "name": func_name,
                    "description": func_metadata.description or f"Function to {func_name}",
                    "inputSchema": {
                        "type": "object",
                        "properties": properties,
                        **({"required": required_params} if required_params else {})
                    }
                })
    
    # Return just the tools array for GET requests
    return {
        "tools": tools_list
    }

## ====================================================

@router.post("/tools/call", status_code=status.HTTP_200_OK, summary="Call a specific tool/function")
async def call_tool(request: MCPToolCallRequest):
    """
    Executes a specific tool function using the MCP format.
    """
    try:
        # Validate method
        if request.method != "tools/call":
            return {
                "jsonrpc": "2.0",
                "id": request.id or 1,
                "error": {
                    "code": -32601,
                    "message": f"Invalid method: {request.method}, expected 'tools/call'"
                }
            }
            
        if not kernel.plugins:
            return {
                "jsonrpc": "2.0",
                "id": request.id or 1,
                "error": {
                    "code": 503,
                    "message": "Kernel plugins not loaded"
                }
            }
        
        # Extract function name and arguments from MCP request
        function_name = request.params.name
        arguments = request.params.arguments or {}
        request_id = request.id or 1
        
        print(f"[MCP] Calling function: {function_name} with arguments: {arguments}")
        
        # Find the plugin containing this function
        plugin_name = None
        kernel_function = None
        
        for p_name, plugin in kernel.plugins.items():
            if function_name in plugin:
                plugin_name = p_name
                kernel_function = plugin[function_name]
                break
        
        # Validate function exists
        if not kernel_function:
            available_functions = []
            for p_name, plugin in kernel.plugins.items():
                for f_name in plugin.functions.keys():
                    available_functions.append(f_name)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": 404,
                    "message": f"Function '{function_name}' not found. Available: {available_functions}"
                }
            }
        
        print(f"[MCP] Found function '{function_name}' in plugin '{plugin_name}'")
        
        # Prepare arguments for the kernel function
        kernel_args = KernelArguments(**arguments)
        
        # Invoke the kernel function
        result = await kernel.invoke(kernel_function, arguments=kernel_args)
        
        # Process the result value
        response_value = result.value
        if not isinstance(response_value, (str, int, float, bool, dict, list, type(None))):
            response_value = str(response_value)
        
        print(f"[MCP] Function result: {response_value}")
        
        # Return in proper MCP format with content array
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text", 
                        "text": str(response_value) if not isinstance(response_value, str) else response_value
                    }
                ]
            }
        }
        
    except Exception as e:
        print(f"[MCP] Error in /mcp/tools/call: {type(e).__name__} - {str(e)}")
        return {
            "jsonrpc": "2.0",
            "id": getattr(request, 'id', 1),
            "error": {
                "code": 500,
                "message": f"An unexpected error occurred: {str(e)}"
            }
        }

## ====================================================

@router.post("/prompts/list", summary="List prompts")
@router.get("/prompts/list", summary="List prompts")
async def prompts_list(request: Optional[dict] = None):
    """Return empty prompts list - this API doesn't provide prompts"""
    request_id = 1
    if request and isinstance(request, dict) and 'id' in request:
        request_id = request['id']
    
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "prompts": []
        }
    }