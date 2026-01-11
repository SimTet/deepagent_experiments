"""Data Analysis Agent - Standalone script for LangGraph deployment.

This module creates a data analysis agent with SQL querying, schema exploration,
and visualization capabilities for working with SQLite databases.

Demonstrates deepagent features:
- Custom domain-specific tools (SQL, charts, analysis)
- Subagent delegation for specialized statistical analysis
- Native filesystem tools for saving reports (via deepagents)
- Native planning tools for complex multi-step analyses (via deepagents)
"""

from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from examples.config import settings
from examples.data_agent.prompts.prompts import (
    DATA_AGENT_INSTRUCTIONS,
    STATISTICIAN_INSTRUCTIONS,
)
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

# Define tools available to both main agent and subagent
data_tools = [explore_schema, query_database, create_chart, analyze_data]

# Create a statistician sub-agent for specialized analysis tasks
# This demonstrates context isolation - the subagent gets its own context window
statistician_subagent = {
    "name": "statistician",
    "model": model,
    "description": "Delegate complex statistical analysis to this specialist. Use for correlation analysis, trend detection, or in-depth data distribution analysis.",
    "system_prompt": STATISTICIAN_INSTRUCTIONS,
    "tools": [query_database, analyze_data],  # Only analysis-focused tools
}

# Create the agent with data analysis tools and subagent
# The agent automatically gets native tools: write_file, read_file, write_todos, etc.
agent = create_deep_agent(
    model=model,
    tools=data_tools,
    system_prompt=DATA_AGENT_INSTRUCTIONS,
    subagents=[statistician_subagent],
)
