"""Gemini LangGraph Agent Example.

This example demonstrates how to wrap the Gemini model in a LangGraph agent using the deepagents framework.
"""

from deepagents import create_deep_agent
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from examples.config import settings


# Define a simple tool
@tool
def get_agent_info() -> str:
    """Returns information about the agent."""
    return "I am a LangGraph agent powered by Gemini, created by deepagents."


# Initialize the Gemini model
# Using the model name from settings, or defaulting to a specific one if needed
model_name = "gemini-2.5-flash"  # Using a standard model name for stability, or could use settings.GOOGLE_MODEL_NAME
if hasattr(settings, "GOOGLE_MODEL_NAME"):
    model_name = settings.GOOGLE_MODEL_NAME

model = ChatGoogleGenerativeAI(model=model_name, temperature=0)

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
