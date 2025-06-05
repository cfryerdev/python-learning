# app/models.py
from typing import Any, Optional, Dict, List
from pydantic import BaseModel, Field, ConfigDict

## ====================================================

class ChatRequest(BaseModel):
    user_query: str
    chat_history: list[dict[str, str]] = []

class ExecuteToolRequest(BaseModel):
    plugin_name: str
    function_name: str
    arguments: dict = {}

## ====================================================

class PersonBaseModel(BaseModel):
    """Base model for person attributes, used for sharing common fields."""
    first_name: str = Field(..., min_length=1, max_length=50, description="Person's first name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Person's last name")
    age: Optional[int] = Field(None, ge=0, le=150, description="Person's age")
    email: Optional[str] = Field(None, max_length=100, description="Person's email address, must be unique if provided")

## ====================================================

class PersonCreateRequest(PersonBaseModel):
    """Model for creating a new person. Inherits all fields from PersonBaseModel."""
    # This class currently inherits all fields and behavior from PersonBaseModel
    # without adding new fields or overriding existing ones. It serves as a specific
    # type hint for creation requests.
    # Specific validation for creation can be added here if needed.
    # For example, making email mandatory on create:
    # email: str = Field(..., max_length=100, description="Person's email address")

## ====================================================

class PersonUpdateRequest(BaseModel):
    """Model for updating an existing person. All fields are optional."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Person's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Person's last name")
    age: Optional[int] = Field(None, ge=0, le=150, description="Person's age")
    email: Optional[str] = Field(None, max_length=100, description="Person's email address, must be unique if provided")

## ====================================================

class PersonResponse(PersonBaseModel):
    """Model for API responses when returning person data."""
    id: int = Field(..., description="Unique identifier for the person")
    model_config = ConfigDict(from_attributes=True)

## ====================================================

class MCPParameter(BaseModel):
    name: str
    description: str
    required: bool = False

## ====================================================

class MCPFunction(BaseModel):
    name: str
    description: str
    parameters: List[MCPParameter]

## ====================================================

class MCPPlugin(BaseModel):
    name: str
    description: str = ""
    functions: List[MCPFunction]

## ====================================================

class MCPClientInfo(BaseModel):
    name: str
    version: str

## ====================================================

class MCPInitializeParams(BaseModel):
    protocolVersion: str = "2024-11-05"
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    clientInfo: MCPClientInfo

## ====================================================

class MCPInitializeRequest(BaseModel):
    method: str
    params: MCPInitializeParams
    id: Optional[int] = None
    jsonrpc: str = "2.0"

## ====================================================

class MCPToolCallParams(BaseModel):
    name: str
    plugin: Optional[str] = None
    arguments: Dict[str, Any] = Field(default_factory=dict)

## ====================================================

class MCPToolCallRequest(BaseModel):
    method: str
    params: MCPToolCallParams
    id: Optional[int] = None
    jsonrpc: str = "2.0"

## ====================================================

class MCPToolsListRequest(BaseModel):
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    id: Optional[int] = None
    jsonrpc: str = "2.0"