# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains example agents built using the `deepagents` framework with LangGraph for orchestration. Each agent demonstrates different capabilities: web research, data analysis, requirements engineering, project kickoff planning, and AI governance assessment.

## Commands

### Environment Setup
```bash
# Install dependencies (uses uv)
uv sync

# Copy and configure environment variables
cp .env_example .env
# Edit .env to add TAVILY_API_KEY and GOOGLE_API_KEY
```

### Running Agents

Agents can be run via:
1. **Jupyter notebooks** - Each agent has an `agent_demo.ipynb` in its directory
2. **LangGraph CLI** - Each agent directory contains a `langgraph.json` for deployment

```bash
# Run with LangGraph CLI (example for simple_agent)
cd examples/simple_agent
langgraph dev
```

## Architecture

### Agent Structure Pattern

Each agent in `examples/` follows this structure:
```
examples/<agent_name>/
├── agent.py           # Main agent definition using create_deep_agent()
├── langgraph.json     # LangGraph deployment config
├── agent_demo.ipynb   # Interactive demo notebook
├── prompts/
│   └── prompts.py     # System prompts and instructions
└── tools/
    └── tools.py       # Custom @tool decorated functions
```

### Creating Agents with deepagents

Agents are created using `create_deep_agent()` from the `deepagents` package:

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model=model,              # LangChain chat model
    tools=[...],              # List of @tool decorated functions
    system_prompt="...",      # Agent instructions
    subagents=[...],          # Optional: list of subagent dicts
)
```

### Subagent Pattern

Subagents enable context isolation and specialized delegation:

```python
subagent = {
    "name": "specialist-name",
    "model": model,
    "description": "When to delegate to this agent",
    "system_prompt": "Agent-specific instructions",
    "tools": [subset_of_tools],
}
```

The main agent orchestrates while subagents handle specialized tasks with their own context windows.

### Native Tools

Agents created with `create_deep_agent` automatically receive native tools including `write_file`, `read_file`, `write_todos` for filesystem access and planning capabilities.

## Configuration

Settings are managed in `examples/config.py` using Pydantic Settings:
- `GOOGLE_API_KEY` - Required for Gemini model
- `TAVILY_API_KEY` - Required for web search
- `GOOGLE_MODEL_NAME` - Defaults to "gemini-2.5-flash"
- `TEMPERATURE` - Defaults to 0.0
- `MAX_CONCURRENT_RESEARCH_UNITS` - Parallel research limit
- `MAX_RESEARCHER_ITERATIONS` - Research depth limit

## Example Agents

- **simple_agent**: Basic demo with date/math tools
- **research_agent**: Web research with Tavily search and strategic thinking
- **data_agent**: SQL querying, schema exploration, and visualization
- **requirements_agent**: Agile requirements engineering with epic/story creation
- **project_kickoff_agent**: Multi-subagent orchestration (architect, task-planner, risk-assessor)
- **ai_governance_agent**: Compliance assessment questionnaire workflow
