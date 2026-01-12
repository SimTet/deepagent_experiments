"""AI Governance Agent - Standalone script for LangGraph deployment.

This module creates an AI governance assessment agent that guides users through
a comprehensive questionnaire covering IT Security, Data Privacy (GDPR),
EU AI Act compliance, and AI Ethics.

Demonstrates deepagent features:
- Custom domain-specific tools (questionnaire management, answer storage)
- Subagent delegation for specialized compliance guidance
- Structured assessment workflow with progress tracking
- Report generation with risk analysis
"""

from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from examples.config import settings
from examples.ai_governance_agent.prompts.prompts import (
    AI_GOVERNANCE_AGENT_INSTRUCTIONS,
    COMPLIANCE_ADVISOR_INSTRUCTIONS,
)
from examples.ai_governance_agent.tools.tools import (
    generate_assessment_report,
    get_assessment_progress,
    get_current_answers,
    get_question,
    load_questionnaire,
    save_answer,
    start_new_assessment,
)

# Initialize the language model
model = ChatGoogleGenerativeAI(
    model=settings.GOOGLE_MODEL_NAME,
    temperature=settings.TEMPERATURE,
    google_api_key=settings.GOOGLE_API_KEY,
)

# Define tools for AI governance assessment
governance_tools = [
    load_questionnaire,
    get_question,
    save_answer,
    get_assessment_progress,
    get_current_answers,
    generate_assessment_report,
    start_new_assessment,
]

# Create a compliance advisor sub-agent for detailed regulatory guidance
# This demonstrates context isolation - the subagent focuses on compliance expertise
compliance_advisor_subagent = {
    "name": "compliance-advisor",
    "model": model,
    "description": "Delegate complex compliance questions to this advisor. Use for detailed guidance on EU AI Act classification, GDPR requirements, or IT security standards.",
    "system_prompt": COMPLIANCE_ADVISOR_INSTRUCTIONS,
    "tools": [],  # No tools needed - pure advisory based on expertise
}

# Create the agent with governance tools and subagent
# The agent automatically gets native tools: write_file, read_file, write_todos, etc.
agent = create_deep_agent(
    model=model,
    tools=governance_tools,
    system_prompt=AI_GOVERNANCE_AGENT_INSTRUCTIONS,
    subagents=[compliance_advisor_subagent],
)
