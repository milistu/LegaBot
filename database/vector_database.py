import json
import subprocess
from pathlib import Path
from typing import Dict, List

import tiktoken
from loguru import logger


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
    output_path: Path, scraped_data: List[Dict], embedding_model: str
) -> None:
    """
    Prepare data for embedding and save to a file.

    Args:
        output_path (Path): The path to save the prepared data.
        scraped_data (List[Dict]): The scraped data to be prepared.
        embedding_model (str): The embedding model to be used.

    Returns:
        None
    """
    jobs = [
        {
            "model": embedding_model,
            "input": f"{sample['title']}: {' '.join(sample['texts'])}",
            "id": id,
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
    Run the API request processor with specified parameters.

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
