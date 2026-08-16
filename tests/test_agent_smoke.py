"""No-network smoke coverage for every Python example agent."""

import importlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from langgraph.graph.state import CompiledStateGraph


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
AGENT_MODULES = (
    "examples.simple_agent.agent",
    "examples.research_agent.agent",
    "examples.data_agent.agent",
    "examples.requirements_agent.agent",
    "examples.project_kickoff_agent.agent",
    "examples.ai_governance_agent.agent",
    "examples.ai_ideation_agent.agent",
    "examples.gemini_langgraph_agent.agent",
)


class AgentSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("GOOGLE_API_KEY", "smoke-test-google-key")
        os.environ.setdefault("TAVILY_API_KEY", "smoke-test-tavily-key")

    def test_each_agent_module_builds_a_graph(self):
        for module_name in AGENT_MODULES:
            with self.subTest(module=module_name):
                module = importlib.import_module(module_name)
                self.assertIsInstance(module.agent, CompiledStateGraph)

    def test_langgraph_graph_paths_resolve_from_repo_root(self):
        for config_path in sorted(REPOSITORY_ROOT.glob("examples/*/langgraph.json")):
            with self.subTest(config=config_path):
                config = json.loads(config_path.read_text(encoding="utf-8"))
                for graph_spec in config["graphs"].values():
                    source_path, attribute = graph_spec.split(":", maxsplit=1)
                    module_path = REPOSITORY_ROOT / source_path
                    self.assertTrue(module_path.is_file(), graph_spec)
                    self.assertTrue(attribute)

    def test_model_factory_passes_validated_credentials_explicitly(self):
        from examples import config

        with patch.object(config, "ChatGoogleGenerativeAI") as constructor:
            config.create_gemini_model()

        constructor.assert_called_once_with(
            model=config.settings.GOOGLE_MODEL_NAME,
            temperature=config.settings.TEMPERATURE,
            google_api_key=config.settings.GOOGLE_API_KEY,
        )


if __name__ == "__main__":
    unittest.main()
