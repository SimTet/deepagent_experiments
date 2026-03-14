"""Simple Agent CLI demo — replaces agent_demo.ipynb.

Usage:
    # Run the preset demo tests
    uv run python -m examples.simple_agent.demo

    # Interactive chat mode
    uv run python -m examples.simple_agent.demo --chat

    # Single query
    uv run python -m examples.simple_agent.demo --query "What is 3.5 times 7.2?"
"""

import argparse
import sys

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

from examples.utils import format_messages, show_prompt

load_dotenv(".env", override=True)

console = Console()


def create_agent():
    """Create and return the simple agent."""
    from deepagents import create_deep_agent
    from langchain_google_genai import ChatGoogleGenerativeAI

    from examples.config import settings
    from examples.simple_agent.prompts.prompts import SIMPLE_AGENT_INSTRUCTIONS
    from examples.simple_agent.tools.tools import (
        divide_floats,
        get_todays_date,
        multiply_floats,
    )

    tools = [get_todays_date, multiply_floats, divide_floats]

    console.print(Rule("Tools"))
    for tool in tools:
        console.print(f"  [bold]{tool.name}[/bold]: {tool.description.splitlines()[0]}")
    console.print()

    console.print(Rule("System Prompt"))
    show_prompt(SIMPLE_AGENT_INSTRUCTIONS)
    console.print()

    model = ChatGoogleGenerativeAI(
        model=settings.GOOGLE_MODEL_NAME, temperature=settings.TEMPERATURE
    )
    agent = create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=SIMPLE_AGENT_INSTRUCTIONS,
    )
    console.print("[green]Agent created successfully.[/green]\n")
    return agent


def invoke(agent, query: str):
    """Invoke the agent with a query and display the result."""
    result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    format_messages(result["messages"])
    return result


def run_demo(agent):
    """Run the preset demo tests (mirrors the notebook cells)."""
    tests = [
        ("What's today's date?", "Get today's date"),
        ("What is 3.5 multiplied by 7.2?", "Multiply 3.5 by 7.2"),
        ("What is 100 divided by 4?", "Divide 100 by 4"),
        ("What is 42 divided by 0?", "Division by zero"),
        (
            "What's today's date? Also, can you calculate 15.5 multiplied by 2.5, "
            "and then divide that result by 5?",
            "Combined query — date and calculation",
        ),
    ]

    for i, (query, label) in enumerate(tests, 1):
        console.print(Rule(f"Test {i}: {label}"))
        invoke(agent, query)
        console.print()


def run_chat(agent):
    """Interactive chat loop."""
    console.print(
        Panel(
            "Type your message and press Enter. Type 'quit' or Ctrl+C to exit.",
            title="Interactive Chat",
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
    parser = argparse.ArgumentParser(description="Simple Agent CLI demo")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--chat", action="store_true", help="Interactive chat mode"
    )
    group.add_argument(
        "--query", "-q", type=str, help="Run a single query"
    )
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
