"""Requirements Agent - Standalone script for LangGraph deployment.

This module creates a requirements engineering agent following agile methodology
for capturing and structuring IT/BI/AI project requirements.
"""

from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from examples.config import settings
from examples.requirements_agent.prompts.prompts import REQUIREMENTS_AGENT_INSTRUCTIONS
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

# Create the agent with requirements tools
agent = create_deep_agent(
    model=model,
    tools=[
        create_epic,
        create_user_story,
        list_requirements,
        refine_requirement,
        generate_requirements_summary,
        interview_stakeholder,
    ],
    system_prompt=REQUIREMENTS_AGENT_INSTRUCTIONS,
)
