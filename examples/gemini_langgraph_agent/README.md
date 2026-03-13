# Gemini LangGraph Agent

This example demonstrates how to create a LangGraph agent using the Google Gemini model within the `deepagents` framework.

## Overview

The `agent.py` script initializes a `ChatGoogleGenerativeAI` model and wraps it using `create_deep_agent`.
This function returns a `CompiledStateGraph`, which is a standard LangGraph object that can be invoked, streamed, or deployed.

## Usage

To run the agent:

```bash
python -m examples.gemini_langgraph_agent.agent
```

## Key Components

- **Model**: Uses `ChatGoogleGenerativeAI` (Gemini).
- **Framework**: Uses `deepagents.create_deep_agent` to build the graph.
- **Tools**: Includes a custom tool `get_agent_info` and standard deepagents tools (file system, etc.).
