import os
from typing import Generator, List, Tuple

import streamlit as st
import yaml
from langfuse.decorators import observe
from loguru import logger
from openai import OpenAI
from pydantic import BaseModel
from qdrant_client import QdrantClient

from database.utils import embed_text, get_context, search
from llm.prompts import DEFAULT_CONTEXT
from llm.utils import get_answer, get_messages
from router.query_router import semantic_query_router
from router.router_prompt import DEFAULT_ROUTER_RESPONSE, ROUTER_PROMPT

LOGO_URL = "assets/Legabot-Logomark.svg"
LOGO_TEXT_URL = "assets/Legabot-Light-Horizontal.svg"
TEXT_URL = "assets/Legabot-Dark-Typography.svg"

WARNING_MESSAGE = """
_Please note that LegaBot may make **mistakes**. For critical legal information, always **verify** with a qualified legal professional. LegaBot is here to assist, not replace professional legal advice._
"""

QUERY_SUGGESTIONS = """
Na koliko dana godisnjeg imam pravo?\n
Da li smem da koristim porodiljsko bolovanje zene umesto nje?\n
Koji porez placam ako sam preduzetnik?\n
Da li mogu da trazim da se izbrisu moji podaci sa sajta ako ih nisam odborio?\n
U kom roku mogu da trazim zamenu proizvoda kojim nisam zadovoljan?\n
Kome pripadaju pokloni koje smo muz i ja dobili na vencanju?
"""

AUTHORS = """
**Attorney:** [Anja Berić](https://www.linkedin.com/in/anja-beric-150285vb/?originalSubdomain=rs)\n
**Research Engineer:** [Milutin Studen](https://www.linkedin.com/in/milutin-studen/)
"""


class RouterConfig(BaseModel):
    model: str
    temperature: float


class ChatConfig(BaseModel):
    model: str
    temperature: float
    max_conversation: int


class EmbeddingsConfig(BaseModel):
    model: str
    dimensions: int


class OpenAIConfig(BaseModel):
    embeddings: EmbeddingsConfig
    chat: ChatConfig
    router: RouterConfig


class Config(BaseModel):
    openai: OpenAIConfig


def load_config(yaml_file_path: str = "./config.yaml") -> Config:
    with open(yaml_file_path, "r") as file:
        yaml_content = yaml.safe_load(file)
    return Config(**yaml_content)


@st.cache_resource
def initialize_clients() -> Tuple[OpenAI, QdrantClient]:
    """
    Initializes and returns the clients for OpenAI and Qdrant services.

    Returns:
    - Tuple[OpenAI, QdrantClient]: A tuple containing the initialized OpenAI and Qdrant clients.

    Raises:
    - EnvironmentError: If required environment variables are missing.
    """
    try:
        # Retrieve Qdrant client configuration from environment variables
        qdrant_url = os.environ["QDRANT_CLUSTER_URL"]
        qdrant_api_key = os.environ["QDRANT_API_KEY"]
        qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

        # Retrieve OpenAI client configuration from environment variables
        openai_api_key = os.environ["OPENAI_API_KEY"]
        openai_client = OpenAI(api_key=openai_api_key)

        return openai_client, qdrant_client
    except KeyError as e:
        error_msg = f"Missing environment variable: {str(e)}"
        logger.error(error_msg)
        raise EnvironmentError(error_msg)


@observe()
def generate_response(
    query: str, openai_client: OpenAI, qdrant_client: QdrantClient, config: Config
) -> Generator[str, None, None]:
    """
    Generates a response for a given user query using a combination of semantic search and a chat model.

    Args:
    - query (str): The user's query string.
    - openai_client (OpenAI): Client to interact with OpenAI's API.
    - qdrant_client (QdrantClient): Client to interact with Qdrant's API.
    - config (Config): Configuration settings for API interaction and response handling.

    Yields:
    - str: Parts of the generated response from the chat model.
    """
    try:
        # Limit the stored messages to the maximum conversation length defined in the configuration
        st.session_state.messages = st.session_state.messages[
            -config.openai.chat.max_conversation :
        ]

        # Embed the user query using the specified model in the configuration
        embedding_response = embed_text(
            client=openai_client,
            text=query,
            model=config.openai.embeddings.model,
        )
        embedding = embedding_response.data[0].embedding

        # Determine the relevant collections to route the query to
        collections = semantic_query_router(
            client=openai_client,
            model=config.openai.router.model,
            query=query,
            prompt=ROUTER_PROMPT,
            temperature=config.openai.router.temperature,
        )
        logger.info(f"Query routed to collections: {collections}")

        # Determine the context for the chat model based on the routed collections
        context = determine_context(collections, embedding, qdrant_client)

        # Generate the response stream from the chat model
        stream = get_answer(
            client=openai_client,
            model=config.openai.chat.model,
            temperature=config.openai.chat.temperature,
            messages=get_messages(
                context=context, query=query, conversation=st.session_state.messages
            ),
            stream=True,
        )

        # Yield each part of the response as it becomes available
        for chunk in stream:
            part = chunk.choices[0].delta.content
            if part is not None:
                yield part

    except Exception as e:
        logger.error(f"An error occurred while generating the response: {str(e)}")
        yield "Sorry, an error occurred while processing your request."


def determine_context(
    collections: List[str], embedding: List[float], qdrant_client: QdrantClient
) -> str:
    """Determines the context for generating responses based on search results from collections."""
    try:
        if collections[0] == DEFAULT_ROUTER_RESPONSE:
            return DEFAULT_CONTEXT
        else:
            search_results = []
            for collection_name in collections:
                search_results.extend(
                    search(
                        client=qdrant_client,
                        collection=collection_name,
                        query_vector=embedding,
                        limit=10,
                        with_vectors=True,
                    )
                )
            # Upgrade this with tokes length checking
            top_k = 15 if len(collections) > 1 else 10
            return get_context(search_results=search_results, top_k=top_k)
    except Exception as e:
        logger.error(f"Error determining context: {str(e)}")
        return DEFAULT_CONTEXT  # Fallback to default context
