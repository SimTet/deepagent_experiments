"""Command-line demo for the AI ideation agent."""

import argparse

from examples.utils import format_messages

DEFAULT_QUERY = "Start an AI use-case canvas for improving employee onboarding."


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Ideation Agent CLI demo")
    parser.add_argument("--query", "-q", default=DEFAULT_QUERY, help="Ideation request")
    args = parser.parse_args()

    from examples.ai_ideation_agent.agent import agent

    result = agent.invoke({"messages": [{"role": "user", "content": args.query}]})
    format_messages(result["messages"])


if __name__ == "__main__":
    main()
