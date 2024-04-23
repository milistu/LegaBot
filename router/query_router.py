from typing import List, Dict
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
