import json
import subprocess
from pathlib import Path
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
from tqdm.auto import tqdm


def create_collection(
    client: QdrantClient,
    name: str,
    vector_size: int = 1536,
    distance: Distance = Distance.COSINE,
) -> bool:
    """Create a collection in Qdrant."""
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
    """Upsert data points into a Qdrant collection."""
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
    Create embeddings using OpenAI API.
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


def load_json(path: Path) -> List[Dict]:
    """
    Load JSON data from a file.

    Args:
        path (Path): The path to the JSON file.

    Returns:
        List[Dict]: The JSON data loaded from the file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not path.exists():
        logger.error(f"File: {path} does not exist.")
        raise FileNotFoundError(f"File: {path} does not exist.")

    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def prepare_for_embedding(
    output_path: Path, scraped_data: List[Dict], model: str
) -> None:
    """
    Prepare data for embedding and save to a file.

    Args:
        output_path (Path): The path to save the prepared data.
        scraped_data (List[Dict]): The scraped data to be prepared.
        model (str): The embedding model to be used.

    Returns:
        None
    """
    jobs = [
        {
            "model": model,
            "id": id,
            "title": sample["title"],
            "link": sample["link"],
            "input": f"{sample['title']}: {' '.join(sample['texts'])}",
        }
        for id, sample in enumerate(scraped_data)
    ]
    with open(output_path, "w", encoding="utf-8") as file:
        for job in jobs:
            json_string = json.dumps(job)
            file.write(json_string + "\n")


def get_token_num(text: str, model_name: str) -> int:
    """
    Get the number of tokens in a text for a given model.

    Args:
        text (str): The input text.
        model_name (str): The name of the model.

    Returns:
        int: The number of tokens in the text.
    """
    enc = tiktoken.encoding_for_model(model_name)
    return len(enc.encode(text))


def run_api_request_processor(
    requests_filepath: Path,
    save_path: Path,
    max_requests_per_minute: int = 2500,
    max_tokens_per_minute: int = 900000,
    token_encoding_name: str = "cl100k_base",
    max_attempts: int = 5,
    logging_level: int = 20,
) -> None:
    """
    Run the API request processor to call the OpenAI API in parallel, creating embeddings with the specified model.

    Args:
        requests_filepath (Path): The path to the requests file.
        save_path (Path): The path to save the results.
        max_requests_per_minute (int): Maximum number of requests per minute.
        max_tokens_per_minute (int): Maximum number of tokens per minute.
        token_encoding_name (str): The name of the token encoding.
        max_attempts (int): Maximum number of attempts for each request.
        logging_level (int): Logging level.

    Returns:
        None
    """
    if not requests_filepath.exists():
        logger.error(f"File {requests_filepath} does not exist.")
        raise FileNotFoundError(f"File {requests_filepath} does not exist.")
    if save_path.suffix != ".jsonl":
        logger.error(f"Save path {save_path} must be JSONL.")
        raise ValueError(f"Save path {save_path} must be JSONL.")

    command = [
        "python",
        "database/api_request_parallel_processor.py",
        "--requests_filepath",
        requests_filepath,
        "--save_filepath",
        save_path,
        "--request_url",
        "https://api.openai.com/v1/embeddings",
        "--max_requests_per_minute",
        str(max_requests_per_minute),
        "--max_tokens_per_minute",
        str(max_tokens_per_minute),
        "--token_encoding_name",
        token_encoding_name,
        "--max_attempts",
        str(max_attempts),
        "--logging_level",
        str(logging_level),
    ]
    result = subprocess.run(command, text=True, capture_output=True)

    if result.returncode == 0:
        logger.info(f"Embeddings saved to: {save_path}")
    else:
        logger.error("Error in Embedding execution!")
        logger.error("Error:", result.stderr)


# Eliminate this or make it more general
def validate_path(path: Path) -> None:
    if not isinstance(path, Path):
        logger.error(f'"{path}" must be a valid Path object')
        raise ValueError(f'"{path}" must be a valid Path object')
    path.mkdir(parents=True, exist_ok=True)


def create_embeddings(
    scraped_dir: Path, to_process_dir: Path, embeddings_dir: Path, model: str
) -> None:
    """
    Embed scraped law files by preparing the data and running the request processor
    to call the OpenAI API in parallel, creating embeddings with the specified model.

    Args:
        scraped_dir (Path): Directory to the law files.
        to_process_dir (Path): Directory to process files.
        embeddings_dir (Path): Directory for storing embeddings.
        model (str): The embedding model to be used.

     Raises:
        ValueError: If any of the provided paths are invalid.
    """
    # Validate input paths
    validate_path(scraped_dir)
    validate_path(to_process_dir)
    validate_path(embeddings_dir)

    scraped_paths = list(scraped_dir.iterdir())

    for file_path in tqdm(
        scraped_paths, desc="Embedding scraped files", total=len(scraped_paths)
    ):
        scraped_data = load_json(path=file_path)

        requests_filepath = to_process_dir / (file_path.stem + ".jsonl")
        prepare_for_embedding(
            output_path=requests_filepath,
            scraped_data=scraped_data,
            model=model,
        )

        processed_filepath = embeddings_dir / requests_filepath.name
        run_api_request_processor(
            requests_filepath=requests_filepath, save_path=processed_filepath
        )


def load_and_process_embeddings(path: Path) -> List[PointStruct]:
    """
    Load embeddings from a JSON lines file and process them into data points.

    Args:
        path (Path): The path to the JSON lines file containing embeddings.

    Returns:
        List[PointStruct]: A list of PointStruct objects containing the processed data.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there is an error reading the file.
        json.JSONDecodeError: If there is an error parsing the JSON.
    """
    if not path.exists():
        logger.error(f"File: {path} does not exist.")
        raise FileNotFoundError(f"File: {path} does not exist.")

    try:
        with open(path, "r", encoding="utf-8") as file:
            embedding_data = [json.loads(line) for line in file]
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Error reading or parsing file: {e}")
        raise

    points = []
    for item in embedding_data:
        try:
            points.append(
                PointStruct(
                    id=item[0]["id"],
                    vector=item[1]["data"][0]["embedding"],
                    payload={
                        "title": item[0]["title"],
                        "text": item[0]["input"],
                        "link": item[0]["link"],
                    },
                )
            )
        except KeyError as e:
            logger.error(f"Missing key in embedded data: {e}")
            continue
    return points
