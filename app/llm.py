# app/llm.py
import os
from openai import OpenAI
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

# Import plugins
from .plugins.create_person_plugin import CreatePersonPlugin
from .plugins.get_person_plugin import GetPersonPlugin
from .plugins.get_people_plugin import GetPeoplePlugin
from .plugins.update_person_plugin import UpdatePersonPlugin
from .plugins.delete_person_plugin import DeletePersonPlugin
from .plugins.system_prompt_plugin import SystemPromptPlugin

## ====================================================

# Initialize OpenAI client (for direct calls, if still needed)
# Environment variables are expected to be loaded by the main application entry point (main.py)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

kernel = Kernel()
kernel.add_service(
    OpenAIChatCompletion(
        service_id="chat-gpt",
        ai_model_id=os.getenv("OPENAI_API_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
)

## ====================================================

# Load plugins into the kernel

# Add each plugin directly to the kernel with the plugin_name="PeopleCRUD"
kernel.add_plugin(CreatePersonPlugin(), plugin_name="PeopleCRUD")
kernel.add_plugin(GetPersonPlugin(), plugin_name="PeopleCRUD")
kernel.add_plugin(GetPeoplePlugin(), plugin_name="PeopleCRUD")
kernel.add_plugin(UpdatePersonPlugin(), plugin_name="PeopleCRUD")
kernel.add_plugin(DeletePersonPlugin(), plugin_name="PeopleCRUD")

# Add the SystemPromptPlugin separately
kernel.add_plugin(SystemPromptPlugin(), plugin_name="SystemGuide")

## ====================================================

async def get_llm_response(prompt: str) -> str:
    """
    Placeholder function to get a response from an LLM (e.g., OpenAI).
    """
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_API_MODEL", "gpt-4o-mini"), # Use model from .env, fallback to gpt-4o-mini
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting LLM response: {e}")
        # Consider raising an HTTPException here for API responses
        return f"Error: Could not get response from LLM. Details: {str(e)}"

## ====================================================

async def process_with_llm_tool(tool_name: str, tool_input: dict) -> dict:
    """
    Placeholder function to simulate an LLM deciding to use a tool
    and processing its output.
    """
    # In a real scenario, this might involve:
    # 1. LLM deciding which tool to call based on user query.
    # 2. Calling the tool (which might be a function in app.plugins).
    # 3. Getting the tool's output.
    # 4. LLM processing the tool's output to formulate a final response.
    return {
        "status": "LLM processed tool output placeholder",
        "tool_used": tool_name,
        "tool_input": tool_input,
        "llm_summary": f"LLM would summarize the output of {tool_name} here."
    }
