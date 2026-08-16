"""Research Agent CLI demo — replaces agent_demo.ipynb.

Usage:
    # Run the preset demo query
    uv run python -m examples.research_agent.demo

    # Interactive chat mode
    uv run python -m examples.research_agent.demo --chat

    # Single query
    uv run python -m examples.research_agent.demo -q "Compare Python vs Rust for CLI tools"
"""

import argparse

from deepagents.backends.utils import file_data_to_string
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from examples.utils import format_messages, show_prompt

load_dotenv(".env", override=True)

console = Console()

DEMO_QUERY = "Wer ist ENTEGA und wofür steht das Unternehmen?"


def create_agent():
    """Create and return the research agent."""
    from datetime import datetime

    from deepagents import create_deep_agent
    from examples.config import create_gemini_model, settings
    from examples.research_agent.prompts.prompts import (
        RESEARCH_WORKFLOW_INSTRUCTIONS,
        RESEARCHER_INSTRUCTIONS,
        SUBAGENT_DELEGATION_INSTRUCTIONS,
    )
    from examples.research_agent.tools.tools import tavily_search, think_tool

    tools = [tavily_search, think_tool]
    current_date = datetime.now().strftime("%Y-%m-%d")
    max_concurrent = settings.MAX_CONCURRENT_RESEARCH_UNITS
    max_iterations = settings.MAX_RESEARCHER_ITERATIONS

    # Show tools
    console.print(Rule("Tools"))
    for tool in tools:
        console.print(f"  [bold]{tool.name}[/bold]: {tool.description.splitlines()[0]}")
    console.print()

    # Build instructions
    instructions = (
        RESEARCH_WORKFLOW_INSTRUCTIONS
        + "\n\n"
        + "=" * 80
        + "\n\n"
        + SUBAGENT_DELEGATION_INSTRUCTIONS.format(
            max_concurrent_research_units=max_concurrent,
            max_researcher_iterations=max_iterations,
        )
    )

    console.print(Rule("System Prompt"))
    show_prompt(instructions)
    console.print()

    model = create_gemini_model()

    research_sub_agent = {
        "name": "research-agent",
        "model": model,
        "description": "Delegate research to the sub-agent researcher. Only give this researcher one topic at a time.",
        "system_prompt": RESEARCHER_INSTRUCTIONS.format(date=current_date),
        "tools": tools,
    }

    agent = create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=instructions,
        subagents=[research_sub_agent],
    )
    console.print("[green]Research agent created successfully.[/green]\n")
    return agent


def invoke(agent, query: str):
    """Invoke the agent with a query and display results."""
    console.print(Panel(query, title="Query", border_style="blue"))
    console.print()

    result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    format_messages(result["messages"])

    # Display generated files (e.g. /final_report.md)
    files = result.get("files", {})
    if files:
        console.print()
        console.print(Rule("Generated Files"))
        for path, data in files.items():
            content = file_data_to_string(data)
            console.print(Panel(content, title=path, border_style="green"))

    return result


def run_demo(agent):
    """Run the preset demo query."""
    console.print(Rule("Demo: Research Query"))
    invoke(agent, DEMO_QUERY)


def run_chat(agent):
    """Interactive chat loop."""
    console.print(
        Panel(
            "Type your research question and press Enter. Type 'quit' or Ctrl+C to exit.",
            title="Interactive Research Chat",
            border_style="green",
        )
    )
    while True:
        try:
            query = console.input("[bold blue]You:[/bold blue] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\nBye!")
            break
        if not query or query.lower() in ("quit", "exit", "q"):
            console.print("Bye!")
            break
        invoke(agent, query)
        console.print()


def main():
    parser = argparse.ArgumentParser(description="Research Agent CLI demo")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--chat", action="store_true", help="Interactive chat mode")
    group.add_argument("--query", "-q", type=str, help="Run a single research query")
    args = parser.parse_args()

    agent = create_agent()

    if args.chat:
        run_chat(agent)
    elif args.query:
        invoke(agent, args.query)
    else:
        run_demo(agent)


if __name__ == "__main__":
    main()
