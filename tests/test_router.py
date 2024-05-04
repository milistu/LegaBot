import os
import unittest
from pathlib import Path

import yaml
from openai import OpenAI

from router.query_router import semantic_query_router
from router.router_prompt import ROUTER_PROMPT


class RouterTest(unittest.TestCase):

    def setUp(self) -> None:
        # Load configuration
        config_path = Path("./config.yaml")
        with config_path.open("r") as file:
            self.config = yaml.safe_load(file)

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
        for query, expected in self.test_queries_sr:
            response = semantic_query_router(
                client=self.openai_client,
                query=query,
                prompt=ROUTER_PROMPT,
                temperature=self.config["openai"]["gpt_model"]["temperature"],
            )
            self.assertIsInstance(response, list)
            self.assertEqual(
                sorted(response), sorted(expected), f"Failed for query: {query}"
            )

    def test_semantic_query_router_en(self) -> None:
        """Test English queries against the router."""
        for query, expected in self.test_queries_en:
            response = semantic_query_router(
                client=self.openai_client,
                query=query,
                prompt=ROUTER_PROMPT,
                temperature=self.config["openai"]["gpt_model"]["temperature"],
            )
            self.assertIsInstance(response, list)
            self.assertEqual(
                sorted(response), sorted(expected), f"Failed for query: {query}"
            )


if __name__ == "__main__":
    unittest.main()
