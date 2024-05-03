import os
import unittest

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    CollectionStatus,
    OptimizersStatusOneOf,
    PointStruct,
    UpdateStatus,
)

from database.utils import (
    create_collection,
    delete_collection,
    embed_text,
    get_collection_info,
    get_count,
    search,
    upsert,
)


class DatabaseTests(unittest.TestCase):

    def setUp(self) -> None:
        self.qdrant_client = QdrantClient(
            url=os.environ["QDRANT_CLUSTER_URL"],
            api_key=os.environ["QDRANT_API_KEY"],
        )
        self.openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        self.embedding_model = "text-embedding-3-small"
        self.embedding_size = 1536
        self.collection_name = "test_collection"
        self.vector_size = 5
        self.distance_metric = Distance.COSINE
        self.num_points = 5
        self.search_id = 3

        vectors = [
            [0.83339819, 0.18442204, 0.73398492, 0.07254654, 0.59678415],
            [0.82178091, 0.62781154, 0.61448299, 0.42460477, 0.17078789],
            [0.40205651, 0.23181339, 0.66545951, 0.63117029, 0.69641706],
            [0.63051502, 0.41224181, 0.34113335, 0.28599009, 0.98405654],
            [0.86858374, 0.96695683, 0.90005845, 0.36327329, 0.05520949],
        ]

        self.sentences = [
            "The quick brown fox jumps over the lazy dog.",
            "Rainy days should be spent at home with a cup of tea.",
            "Exploring the cosmos challenges both our imaginations and our capabilities.",
            "Every moment is a fresh beginning.",
            "Technology shapes the future of society.",
        ]

        self.points = [
            PointStruct(
                id=i,
                vector=vectors[i],
                payload={"text": "good" if i == self.search_id else "bad"},
            )
            for i in range(self.num_points)
        ]

    def test_01_create_collection(self) -> None:
        result = create_collection(
            client=self.qdrant_client,
            name=self.collection_name,
            vector_size=self.vector_size,
            distance=self.distance_metric,
        )
        self.assertTrue(result)

    def test_02_upsert(self) -> None:
        result = upsert(
            client=self.qdrant_client,
            collection=self.collection_name,
            points=self.points,
        )
        self.assertEqual(
            get_count(client=self.qdrant_client, collection=self.collection_name),
            self.num_points,
        )
        self.assertEqual(result.status, UpdateStatus.COMPLETED)

    def test_03_get_collection_info(self) -> None:
        result = get_collection_info(
            client=self.qdrant_client, collection=self.collection_name
        )
        self.assertEqual(result.status, CollectionStatus.GREEN)
        self.assertEqual(result.optimizer_status, OptimizersStatusOneOf.OK)
        self.assertEqual(result.config.params.vectors.size, self.vector_size)
        self.assertEqual(result.config.params.vectors.distance, self.distance_metric)
        self.assertEqual(result.vectors_count, self.num_points)

    def test_04_search(self) -> None:
        vector = self.points[self.search_id].vector
        result = search(
            client=self.qdrant_client,
            collection=self.collection_name,
            query_vector=vector,
        )
        self.assertEqual(result[0].id, self.search_id)
        self.assertEqual(result[0].payload["text"], "good")

    def test_05_delete_collection(self) -> None:
        result = delete_collection(
            client=self.qdrant_client, collection=self.collection_name
        )
        self.assertTrue(result)

    def test_06_embed_text(self) -> None:
        result = embed_text(
            client=self.openai_client, text=self.sentences, model=self.embedding_model
        )

        self.assertEqual(len(result.data), len(self.sentences))
        self.assertEqual(len(result.data[0].embedding), self.embedding_size)


if __name__ == "__main__":
    unittest.main()
