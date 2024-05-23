import argparse
import json
from pathlib import Path

from loguru import logger
from .utils import create_embeddings


def main(args: argparse.Namespace) -> None:
    logger.info("Creating embeddings.")
    create_embeddings(
        scraped_dir=args.scraped_dir,
        to_process_dir=args.to_process_dir,
        embeddings_dir=args.embeddings_dir,
        model=args.model,
    )
    logger.info("Creating vector database.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create embeddings and vector database for scraped files."
    )
    parser.add_argument(
        "scraped_dir", type=Path, help="Directory to the scraped files."
    )
    parser.add_argument("to_process_dir", type=Path, help="Directory to process files.")
    parser.add_argument(
        "embeddings_dir", type=Path, help="Directory for storing embeddings."
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
