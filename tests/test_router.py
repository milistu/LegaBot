import os
import unittest
from pathlib import Path
from typing import List

from openai import OpenAI

from router.query_router import semantic_query_router
from router.router_prompt import ROUTER_PROMPT
from utils import load_config


class RouterTest(unittest.TestCase):

    def setUp(self) -> None:
        # Load configuration
        config_path = Path("./config.yaml")
        self.config = load_config(yaml_file_path=config_path)

        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

        # Define test cases for both Serbian and English queries
        self.test_queries_sr = [
            (
                "Da li mogu da tražim alimentaciju ako se razvedem?",
                ["porodicni_zakon"],
            ),
            (
                "Kako da zaštitim svoje podatke na internetu?",
                ["zakon_o_zastiti_podataka_o_licnosti"],
                # ["zakon_o_zastiti_podataka_o_licnosti", "zakon_o_zastiti_potrosaca"],
            ),
            (
                "Šta su moja prava kao potrošača i lica na koje se podaci odnose kada kupujem online?",
                ["zakon_o_zastiti_potrosaca", "zakon_o_zastiti_podataka_o_licnosti"],
            ),
            ("Koliko je sati?", ["nema_zakona"]),
            ("Koja su prava zaposlenih na bolovanje?", ["zakon_o_radu"]),
        ]
        self.test_queries_en = [
            (
                "Can I ask for alimony if I get divorced?",
                ["porodicni_zakon"],
            ),
            (
                "How can I protect my data online?",
                ["zakon_o_zastiti_podataka_o_licnosti"],
                # ["zakon_o_zastiti_podataka_o_licnosti", "zakon_o_zastiti_potrosaca"],
            ),
            (
                "What are my rights as a consumer and data subject when shopping online?",
                ["zakon_o_zastiti_potrosaca", "zakon_o_zastiti_podataka_o_licnosti"],
            ),
            ("What time is it?", ["nema_zakona"]),
            ("What are the rights of employees on medical leave?", ["zakon_o_radu"]),
        ]

    def test_semantic_query_router_sr(self) -> None:
        """Test Serbian queries against the router."""
        self._test_query_router(self.test_queries_sr)

    def test_semantic_query_router_en(self) -> None:
        """Test English queries against the router."""
        self._test_query_router(self.test_queries_en)

    def _test_query_router(self, test_queries) -> None:
        """Helper method to test query router functionality."""
        for query, expected in test_queries:
            response = self._route_query(query)
            self.assertIsInstance(response, list)
            self.assertEqual(
                sorted(response), sorted(expected), f"Failed for query: {query}"
            )

    def _route_query(self, query) -> List[str]:
        """Route the query and return the response."""
        return semantic_query_router(
            client=self.openai_client,
            query=query,
            prompt=ROUTER_PROMPT,
            model=self.config.openai.router.model,
            temperature=self.config.openai.router.temperature,
        )


if __name__ == "__main__":
    unittest.main()
