"""Command-line demo for the project kickoff agent."""

import argparse

from examples.utils import format_messages

DEFAULT_QUERY = "Create a kickoff plan for launching an internal knowledge-search assistant."


def main() -> None:
    parser = argparse.ArgumentParser(description="Project Kickoff Agent CLI demo")
    parser.add_argument("--query", "-q", default=DEFAULT_QUERY, help="Project kickoff request")
    args = parser.parse_args()

    from examples.project_kickoff_agent.agent import agent

    result = agent.invoke({"messages": [{"role": "user", "content": args.query}]})
    format_messages(result["messages"])


if __name__ == "__main__":
    main()
