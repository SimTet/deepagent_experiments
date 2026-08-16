"""Command-line demo for the AI governance assessment agent."""

import argparse

from examples.utils import format_messages

DEFAULT_QUERY = "Start an AI governance assessment for a customer-support chatbot."


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Governance Agent CLI demo")
    parser.add_argument("--query", "-q", default=DEFAULT_QUERY, help="Assessment request")
    args = parser.parse_args()

    from examples.ai_governance_agent.agent import agent

    result = agent.invoke({"messages": [{"role": "user", "content": args.query}]})
    format_messages(result["messages"])


if __name__ == "__main__":
    main()
