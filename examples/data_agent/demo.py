"""Command-line demo for the data analysis agent."""

import argparse

from examples.utils import format_messages

DEFAULT_QUERY = "Describe the available SQLite data and suggest one useful analysis."


def main() -> None:
    parser = argparse.ArgumentParser(description="Data Analysis Agent CLI demo")
    parser.add_argument("--query", "-q", default=DEFAULT_QUERY, help="Analysis request")
    args = parser.parse_args()

    from examples.data_agent.agent import agent

    result = agent.invoke({"messages": [{"role": "user", "content": args.query}]})
    format_messages(result["messages"])


if __name__ == "__main__":
    main()
