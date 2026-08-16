"""Command-line demo for the requirements engineering agent."""

import argparse

from examples.utils import format_messages

DEFAULT_QUERY = "Help me outline an epic for a customer self-service analytics portal."


def main() -> None:
    parser = argparse.ArgumentParser(description="Requirements Agent CLI demo")
    parser.add_argument("--query", "-q", default=DEFAULT_QUERY, help="Requirements request")
    args = parser.parse_args()

    from examples.requirements_agent.agent import agent

    result = agent.invoke({"messages": [{"role": "user", "content": args.query}]})
    format_messages(result["messages"])


if __name__ == "__main__":
    main()
