"""Simple Agent - Standalone script for LangGraph deployment.

This module creates a simple agent with basic utility tools to demonstrate
tool usage in the deepagents framework.

This is intentionally minimal to show the basics. Note that create_deep_agent
automatically provides additional native tools (write_file, read_file,
write_todos, etc.) - see data_agent and requirements_agent for examples
leveraging these features.
"""

from deepagents import create_deep_agent

from examples.config import create_gemini_model
from examples.simple_agent.prompts.prompts import SIMPLE_AGENT_INSTRUCTIONS
from examples.simple_agent.tools.tools import divide_floats, get_todays_date, multiply_floats

# Initialize the language model
model = create_gemini_model()

# Create the agent with basic tools
agent = create_deep_agent(
    model=model,
    tools=[get_todays_date, multiply_floats, divide_floats],
    system_prompt=SIMPLE_AGENT_INSTRUCTIONS,
)
