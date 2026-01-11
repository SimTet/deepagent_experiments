"""Requirements Agent - Standalone script for LangGraph deployment.

This module creates a requirements engineering agent following agile methodology
for capturing and structuring IT/BI/AI project requirements.

Demonstrates deepagent features:
- Custom domain-specific tools (epic/story creation, refinement)
- Subagent delegation for specialized stakeholder analysis
- Native filesystem tools for additional documentation (via deepagents)
- Native planning tools for complex requirements sessions (via deepagents)
"""

from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from examples.config import settings
from examples.requirements_agent.prompts.prompts import (
    REQUIREMENTS_AGENT_INSTRUCTIONS,
    STAKEHOLDER_ANALYST_INSTRUCTIONS,
)
from examples.requirements_agent.tools.tools import (
    create_epic,
    create_user_story,
    generate_requirements_summary,
    interview_stakeholder,
    list_requirements,
    refine_requirement,
)

# Initialize the language model
model = ChatGoogleGenerativeAI(
    model=settings.GOOGLE_MODEL_NAME,
    temperature=settings.TEMPERATURE,
)

# Define tools for requirements management
requirements_tools = [
    create_epic,
    create_user_story,
    list_requirements,
    refine_requirement,
    generate_requirements_summary,
    interview_stakeholder,
]

# Create a stakeholder analyst sub-agent for deep-dive interviews
# This demonstrates context isolation - the subagent focuses on elicitation
stakeholder_analyst_subagent = {
    "name": "stakeholder-analyst",
    "model": model,
    "description": "Delegate complex stakeholder interviews to this analyst. Use for deep-dive requirements elicitation on specific domains or when exploring unfamiliar business areas.",
    "system_prompt": STAKEHOLDER_ANALYST_INSTRUCTIONS,
    "tools": [interview_stakeholder],  # Only interview tool for focused conversations
}

# Create the agent with requirements tools and subagent
# The agent automatically gets native tools: write_file, read_file, write_todos, etc.
agent = create_deep_agent(
    model=model,
    tools=requirements_tools,
    system_prompt=REQUIREMENTS_AGENT_INSTRUCTIONS,
    subagents=[stakeholder_analyst_subagent],
)
