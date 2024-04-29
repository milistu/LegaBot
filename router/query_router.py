import json
from typing import Dict, List
from openai import OpenAI

import numpy as np


def rout_query(centroids: Dict[str, List], query_embedding: List) -> str:
    centroids = list(centroids.items())
    centroids_np = np.array([value for key, value in centroids])
    query_np = np.array(query_embedding)

    norm_query = np.linalg.norm(query_np)
    norm_centroids = np.linalg.norm(centroids_np, axis=1)

    cosine_similarities = np.dot(centroids_np, query_np) / (norm_centroids * norm_query)
    max_index = np.argmax(cosine_similarities)

    collection = centroids[max_index][0]
    return collection


def semantic_query_router(
    client: OpenAI,
    query: str,
    prompt: str,
    temperature: float,
    model: str = "gpt-3.5-turbo",
) -> List[str]:
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": prompt.format(query=query)}],
        temperature=temperature,
    )
    collections = json.loads(response.choices[0].message.content)["response"]
    return collections
