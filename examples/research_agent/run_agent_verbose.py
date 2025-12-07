import logging

from agent import agent
from langchain_google_genai import ChatGoogleGenerativeAI

from examples.config import settings

logging.basicConfig(level=logging.INFO)


def main():
    logging.info("Invoking agent")
    result = agent.invoke(
        input={
            "messages": [
                {
                    "role": "user",
                    "content": "propose a state of the art agentic solution to use RAG in an corporate environment with multimodal data. include things like hybrid retrieval, reranking and some other useful techniques like pre-structuring data, use metadata, for example as filters etc.",
                }
            ]
        }
    )
    logging.info("Agent invocation complete")
    print(result["messages"][-1])


if __name__ == "__main__":
    main()
