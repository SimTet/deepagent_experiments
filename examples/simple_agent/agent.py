"""Simple Agent - Standalone script for LangGraph deployment.

This module creates a simple agent with basic utility tools to demonstrate
tool usage in the deepagents framework.
"""

from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from examples.config import settings
from examples.simple_agent.prompts.prompts import SIMPLE_AGENT_INSTRUCTIONS
from examples.simple_agent.tools.tools import divide_floats, get_todays_date, multiply_floats

# Initialize the language model
model = ChatGoogleGenerativeAI(model=settings.GOOGLE_MODEL_NAME, temperature=settings.TEMPERATURE)

# Create the agent with basic tools
agent = create_deep_agent(
    model=model,
    tools=[get_todays_date, multiply_floats, divide_floats],
    system_prompt=SIMPLE_AGENT_INSTRUCTIONS,
)
