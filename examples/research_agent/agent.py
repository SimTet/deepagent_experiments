"""Research Agent - Standalone script for LangGraph deployment.

This module creates a deep research agent with custom tools and prompts
for conducting web research with strategic thinking and context management.
"""

from datetime import datetime

from deepagents import create_deep_agent

from examples.config import create_gemini_model, settings
from examples.research_agent.prompts.prompts import (
    RESEARCH_WORKFLOW_INSTRUCTIONS,
    RESEARCHER_INSTRUCTIONS,
    SUBAGENT_DELEGATION_INSTRUCTIONS,
)

if not settings.TAVILY_API_KEY.strip():
    raise ValueError(
        "TAVILY_API_KEY is empty. Edit .env (copied from .env_example) and set a "
        "real value for TAVILY_API_KEY — research_agent requires it for web search."
    )

from examples.research_agent.tools.tools import tavily_search, think_tool  # noqa: E402

# Limits
max_concurrent_research_units = settings.MAX_CONCURRENT_RESEARCH_UNITS
max_researcher_iterations = settings.MAX_RESEARCHER_ITERATIONS

# Get current date
current_date = datetime.now().strftime("%Y-%m-%d")

# Combine orchestrator instructions (RESEARCHER_INSTRUCTIONS only for sub-agents)
INSTRUCTIONS = (
    RESEARCH_WORKFLOW_INSTRUCTIONS
    + "\n\n"
    + "=" * 80
    + "\n\n"
    + SUBAGENT_DELEGATION_INSTRUCTIONS.format(
        max_concurrent_research_units=max_concurrent_research_units,
        max_researcher_iterations=max_researcher_iterations,
    )
)

# Initialize the language model
model = create_gemini_model()

# Create research sub-agent
research_sub_agent = {
    "name": "research-agent",
    "model": model,
    "description": "Delegate research to the sub-agent researcher. Only give this researcher one topic at a time.",
    "system_prompt": RESEARCHER_INSTRUCTIONS.format(date=current_date),
    "tools": [tavily_search, think_tool],
}


# Create the agent
agent = create_deep_agent(
    model=model,
    tools=[tavily_search, think_tool],
    system_prompt=INSTRUCTIONS,
    subagents=[research_sub_agent],
)
