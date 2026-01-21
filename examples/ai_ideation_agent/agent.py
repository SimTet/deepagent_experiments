"""AI Ideation Agent - Demonstrates planning and orchestration in deepagents.

This agent showcases the power of deepagents by:
1. PLANNING: Using write_todos to plan the ideation session before executing
2. GUIDING: Leading users through a 9-section AI Use Case Canvas conversationally
3. DELEGATING: Using specialized subagents for compliance analysis
4. SYNTHESIZING: Combining inputs into exportable deliverables (Markdown + Jira Epic)

The workflow demonstrates clear separation between:
- Orchestration (main agent plans and guides user interaction)
- Execution (main agent collects canvas data, subagent analyzes compliance)
- Synthesis (main agent generates final exports)

Subagents:
- compliance-advisor: Analyzes EU AI Act, GDPR, and IT Security implications
"""

from deepagents import create_deep_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from examples.config import settings
from examples.ai_ideation_agent.prompts.prompts import (
    AI_IDEATION_AGENT_INSTRUCTIONS,
    COMPLIANCE_ADVISOR_INSTRUCTIONS,
)
from examples.ai_ideation_agent.tools.tools import (
    assess_compliance_flags,
    generate_canvas_export,
    get_canvas_answers,
    get_canvas_overview,
    get_canvas_progress,
    get_question,
    get_section,
    save_answer,
    save_section_answers,
    start_new_canvas,
)

# Initialize the language model
model = ChatGoogleGenerativeAI(
    model=settings.GOOGLE_MODEL_NAME,
    temperature=settings.TEMPERATURE,
    google_api_key=settings.GOOGLE_API_KEY,
)

# -----------------------------------------------------------------------------
# TOOLS FOR ORCHESTRATOR
# Organized by workflow phase for clarity
# -----------------------------------------------------------------------------
orchestrator_tools = [
    # Phase 1: Initialize
    start_new_canvas,
    # Phase 2: Navigate & Collect
    get_canvas_overview,
    get_section,
    get_question,
    save_answer,
    save_section_answers,
    # Phase 3: Track Progress
    get_canvas_progress,
    get_canvas_answers,
    # Phase 4: Assess & Export
    assess_compliance_flags,
    generate_canvas_export,
]

# -----------------------------------------------------------------------------
# SUBAGENT DEFINITIONS
# Each subagent is a specialist that handles specific delegated tasks
# -----------------------------------------------------------------------------

# Compliance advisor subagent - analyzes regulatory implications
# Delegated after sections 6-8 are completed to provide detailed guidance
compliance_advisor_subagent = {
    "name": "compliance-advisor",
    "model": model,
    "description": (
        "Delegate compliance analysis to this specialist AFTER completing sections 6-8. "
        "The advisor analyzes EU AI Act risk classification, GDPR implications, "
        "and IT security requirements, providing detailed guidance and recommendations."
    ),
    "system_prompt": COMPLIANCE_ADVISOR_INSTRUCTIONS,
    "tools": [assess_compliance_flags],  # Can assess the collected compliance data
}

# -----------------------------------------------------------------------------
# MAIN AGENT CREATION
# The orchestrator coordinates the entire ideation process
# Native tools (write_todos, task, write_file, read_file) are automatically added
# -----------------------------------------------------------------------------

agent = create_deep_agent(
    model=model,
    tools=orchestrator_tools,
    system_prompt=AI_IDEATION_AGENT_INSTRUCTIONS,
    subagents=[compliance_advisor_subagent],
)
