"""Project Kickoff Agent - Demonstrates planning and execution separation in deepagents.

This agent showcases the power of deepagents by:
1. PLANNING: Using write_todos to plan work before executing
2. DELEGATION: Using specialized subagents for different aspects
3. ARTIFACTS: Using filesystem tools to create persistent deliverables
4. SYNTHESIS: Combining subagent outputs into a cohesive project plan

The workflow demonstrates clear separation between:
- Orchestration (main agent plans and coordinates)
- Execution (subagents do specialized work)
- Synthesis (main agent combines results)

Subagents:
- architect: Designs technical architecture
- task-planner: Creates work breakdown structure
- risk-assessor: Identifies and assesses project risks
"""

from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from examples.config import settings
from examples.project_kickoff_agent.prompts.prompts import (
    ARCHITECT_INSTRUCTIONS,
    ORCHESTRATOR_INSTRUCTIONS,
    RISK_ASSESSOR_INSTRUCTIONS,
    TASK_PLANNER_INSTRUCTIONS,
)
from examples.project_kickoff_agent.tools.tools import (
    get_deliverable_template,
    validate_project_plan,
)

# Initialize the language model
model = ChatGoogleGenerativeAI(
    model=settings.GOOGLE_MODEL_NAME,
    temperature=settings.TEMPERATURE,
)

# Custom tools for the orchestrator
orchestrator_tools = [get_deliverable_template, validate_project_plan]

# -----------------------------------------------------------------------------
# SUBAGENT DEFINITIONS
# Each subagent is a specialist that produces specific deliverables
# -----------------------------------------------------------------------------

# Architect subagent - designs technical architecture
architect_subagent = {
    "name": "architect",
    "model": model,
    "description": (
        "Delegate architecture design to this specialist. "
        "The architect analyzes requirements and creates /docs/architecture.md "
        "with system design, component breakdown, and technology stack."
    ),
    "system_prompt": ARCHITECT_INSTRUCTIONS,
    "tools": [get_deliverable_template],  # Can use template for consistent structure
}

# Task planner subagent - creates work breakdown
task_planner_subagent = {
    "name": "task-planner",
    "model": model,
    "description": (
        "Delegate task breakdown to this specialist. "
        "The task planner creates /docs/tasks.md with epics, tasks, "
        "dependencies, timeline, and team recommendations."
    ),
    "system_prompt": TASK_PLANNER_INSTRUCTIONS,
    "tools": [get_deliverable_template],
}

# Risk assessor subagent - identifies and assesses risks
risk_assessor_subagent = {
    "name": "risk-assessor",
    "model": model,
    "description": (
        "Delegate risk assessment to this specialist. "
        "The risk assessor creates /docs/risks.md with risk register, "
        "risk matrix, mitigation strategies, and response plan."
    ),
    "system_prompt": RISK_ASSESSOR_INSTRUCTIONS,
    "tools": [get_deliverable_template],
}

# -----------------------------------------------------------------------------
# MAIN AGENT CREATION
# The orchestrator coordinates the entire project kickoff process
# -----------------------------------------------------------------------------

agent = create_deep_agent(
    model=model,
    tools=orchestrator_tools,
    system_prompt=ORCHESTRATOR_INSTRUCTIONS,
    subagents=[
        architect_subagent,
        task_planner_subagent,
        risk_assessor_subagent,
    ],
)
