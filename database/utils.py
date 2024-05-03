from typing import Dict, List, Union

import numpy as np
import tiktoken
from loguru import logger
from openai import OpenAI
from openai.types import CreateEmbeddingResponse
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    Filter,
    PointStruct,
    ScoredPoint,
    UpdateResult,
    VectorParams,
)


def create_collection(
    client: QdrantClient,
    name: str,
    vector_size: int = 1536,
    distance: Distance = Distance.COSINE,
) -> bool:
    logger.info(f'Creating collection: "{name}" with vector size: {vector_size}.')
    return client.recreate_collection(
        collection_name=name,
        vectors_config=VectorParams(size=vector_size, distance=distance),
    )


def delete_collection(
    client: QdrantClient, collection: str, timeout: int = None
) -> bool:
    logger.info(f'Deleting collection: "{collection}".')
    return client.delete_collection(collection_name=collection, timeout=timeout)


def get_collection_info(client: QdrantClient, collection: str) -> Dict:
    return client.get_collection(collection_name=collection)


def get_count(client: QdrantClient, collection: str) -> int:
    return client.count(collection_name=collection).count


def upsert(
    client: QdrantClient,
    collection: str,
    points: List[PointStruct],
) -> UpdateResult:
    return client.upsert(collection_name=collection, points=points)


def num_tokens_from_string(string: str, model: str) -> int:
    """Returns the number of tokens in a text string."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.info("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def search(
    client: QdrantClient,
    collection: str,
    query_vector: Union[list, tuple, np.ndarray],
    limit: int = 10,
    query_filter: Filter = None,
    with_vectors: bool = False,
) -> List:
    return client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=limit,
        with_vectors=with_vectors,
        query_filter=query_filter,
    )


def embed_text(
    client: OpenAI, text: Union[str, list], model: str
) -> CreateEmbeddingResponse:
    """
    - Default model (OpenAI): text-embedding-3-small
    - Max input Tokens: 8191
    - TikToken model: cl100k_base
    - Embedding size: 1536
    """
    response = client.embeddings.create(input=text, model=model)
    return response


def format_context(payload: dict) -> str:
    text = f"Naslov: {payload['title']}\n"
    text += f"Link do člana: {payload['link']}\n"
    text += f"{payload['text']}\n\n"
    return text


def get_context(search_results: List[ScoredPoint], top_k: int = None) -> str:
    if top_k is not None:
        search_results = sorted(search_results, key=lambda x: x.score, reverse=True)[
            :top_k
        ]
    return "\n".join([format_context(point.payload) for point in search_results])
