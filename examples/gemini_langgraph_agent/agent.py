"""Gemini LangGraph Agent Example.

This example demonstrates how to wrap the Gemini model in a LangGraph agent using the deepagents framework.
"""

from deepagents import create_deep_agent
from langchain_core.tools import tool

from examples.config import create_gemini_model, settings


# Define a simple tool
@tool
def get_agent_info() -> str:
    """Returns information about the agent."""
    return "I am a LangGraph agent powered by Gemini, created by deepagents."


# Initialize the Gemini model through the shared, credential-explicit helper.
model_name = settings.GOOGLE_MODEL_NAME
model = create_gemini_model()

# Create the deep agent (which returns a CompiledStateGraph)
agent = create_deep_agent(
    model=model,
    tools=[get_agent_info],
    system_prompt="You are a helpful AI assistant powered by Gemini and running as a LangGraph agent.",
)

if __name__ == "__main__":
    # Simple test run
    print(f"Running agent with model: {model_name}")
    response = agent.invoke({"messages": [("user", "Who are you?")]})
    print(response["messages"][-1].content)
