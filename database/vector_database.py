import argparse
import json
import os
from pathlib import Path

from loguru import logger
from qdrant_client import QdrantClient
from tqdm.auto import tqdm

from database.utils import (
    create_collection,
    create_embeddings,
    get_count,
    load_and_process_embeddings,
    upsert,
)


def main(args: argparse.Namespace) -> None:
    logger.info("Creating embeddings.")
    create_embeddings(
        scraped_dir=args.scraped_dir,
        to_process_dir=args.to_process_dir,
        embeddings_dir=args.embeddings_dir,
        model=args.model,
    )

    logger.info("Creating vector database.")
    qdrant_client = QdrantClient(
        url=os.environ["QDRANT_CLUSTER_URL"],
        api_key=os.environ["QDRANT_API_KEY"],
    )
    data_paths = list(args.embeddings_dir.iterdir())
    for path in tqdm(data_paths, total=len(data_paths), desc="Creating collections"):
        # Check if this is necessary
        collection_name = path.stem.replace("-", "_")
        collection_name = collection_name + "_TESTIC"
        points = load_and_process_embeddings(path=path)

        create_collection(client=qdrant_client, name=collection_name)
        upsert(client=qdrant_client, collection=collection_name, points=points)

        point_num = get_count(client=qdrant_client, collection=collection_name)
        if not point_num == len(points):
            logger.error(f"There are missing points in {collection_name} collection.")

        logger.info(
            f'Created "{collection_name}" collection with {point_num} data points.'
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create embeddings and vector database for scraped files."
    )
    parser.add_argument(
        "--scraped_dir", type=Path, help="Directory to the scraped files."
    )
    parser.add_argument(
        "--to_process_dir",
        type=Path,
        default=Path("./database/to_process"),
        help="Directory to process files.",
    )
    parser.add_argument(
        "--embeddings_dir",
        type=Path,
        default=Path("./database/embeddings"),
        help="Directory for storing embeddings.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="The embedding model to be used. If not set, it will be loaded from the config file.",
    )

    args = parser.parse_args()

    # Load model from config file if not explicitly set
    if args.model is None:
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
            args.model = config.get("embedding_model", "default_model")

    main(args=args)
