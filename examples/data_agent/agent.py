"""Data Analysis Agent - Standalone script for LangGraph deployment.

This module creates a data analysis agent with SQL querying, schema exploration,
and visualization capabilities for working with SQLite databases.
"""

from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from examples.config import settings
from examples.data_agent.prompts.prompts import DATA_AGENT_INSTRUCTIONS
from examples.data_agent.tools.tools import (
    analyze_data,
    create_chart,
    explore_schema,
    query_database,
)

# Initialize the language model
model = ChatGoogleGenerativeAI(
    model=settings.GOOGLE_MODEL_NAME,
    temperature=settings.TEMPERATURE,
)

# Create the agent with data analysis tools
agent = create_deep_agent(
    model=model,
    tools=[explore_schema, query_database, create_chart, analyze_data],
    system_prompt=DATA_AGENT_INSTRUCTIONS,
)
