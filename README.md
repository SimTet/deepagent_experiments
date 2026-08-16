# deepagent_experiments

Example agents built with [DeepAgents](https://github.com/langchain-ai/deepagents), a framework for
building planning, file-system-aware, subagent-delegating LLM agents on top of
[LangGraph](https://langchain-ai.github.io/langgraph/) (LangChain's agent orchestration library). Each
example is a small, runnable demo of a different DeepAgents capability.

## Example agents

| Agent | Demonstrates |
|---|---|
| `simple_agent` | Minimal DeepAgents setup with basic utility tools |
| `research_agent` | Web research with Tavily search and strategic multi-step thinking |
| `data_agent` | SQL querying, schema exploration, and chart generation over a SQLite database |
| `requirements_agent` | Agile requirements engineering (epics/user stories) with a stakeholder-analyst subagent |
| `project_kickoff_agent` | Multi-subagent orchestration (architect, task-planner, risk-assessor) with planning-before-execution |
| `ai_governance_agent` | AI governance/compliance assessment via a guided questionnaire (EU AI Act, GDPR, IT security) |
| `ai_ideation_agent` | Guided AI use-case ideation with a compliance-advisor subagent and exportable deliverables |
| `gemini_langgraph_agent` | Bare-bones Gemini + DeepAgents wiring, no LangGraph deployment config |
| `gemini_mcp_agent` | Config bundle (not a Python agent) for driving `gemini-cli` headless mode against the MS365 Graph MCP server |

Reusable MCP servers (used by some of the agents above, and standalone) live in `mcp_servers/` — see
`mcp_servers/README.md`.

## Prerequisites

- Python `>=3.13` (see `pyproject.toml`)
- [`uv`](https://docs.astral.sh/uv/) for dependency management
- API keys:
  - `GOOGLE_API_KEY` — required by every Python agent (all use Gemini). Get one at
    https://aistudio.google.com/apikey
  - `TAVILY_API_KEY` — required only by `research_agent`. Get one at https://app.tavily.com

## Quickstart

```bash
uv sync
cp .env_example .env
# now edit .env and fill in real values for GOOGLE_API_KEY (and TAVILY_API_KEY if you'll run research_agent)

# run any example from the repo root, e.g. simple_agent:
uv run langgraph dev --config examples/simple_agent/langgraph.json
```

This starts LangGraph's local dev server and opens LangGraph Studio in your browser. Swap the
`--config` path to run a different example, e.g. `examples/data_agent/langgraph.json`. All
examples with a `langgraph.json` must be launched this way, from the repo root — running
`langgraph dev` from inside an example's own directory will not find the agent code.

`gemini_langgraph_agent` has no `langgraph.json`; run it directly instead:

```bash
uv run python -m examples.gemini_langgraph_agent.agent
```

`gemini_mcp_agent` isn't a Python agent — see `examples/gemini_mcp_agent/README.md` for its
`gemini-cli` + MCP setup.

If `examples/config.py` can't find a real (non-empty) value for a required key, it raises a clear
`ValidationError` naming the missing variable — check that you edited `.env` and didn't just copy
`.env_example` as-is.
