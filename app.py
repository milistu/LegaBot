from pathlib import Path

import yaml
from taipy.gui import Gui, State, notify

from llm.prompts import context_prompt, query_prompt, system_prompt
from llm.utils import get_answer
from database.utils import embed_text, search, get_context

config_path = Path("./config.yaml")

with config_path.open("r") as file:
    config = yaml.safe_load(file)


def request(query: str) -> str:
    """
    Send a prompt to the GPT API and return the response.

    Args:
        - state: The current state.
        - prompt: The prompt to send to the API.

    Returns:
        The response from the API.
    """
    embedding_response = embed_text(
        text=query, model=config["openai"]["embedding_model"]["name"]
    )
    embedding = embedding_response.data[0].embedding

    search_results = search(
        collection=config["collection"]["name"],
        query_vector=embedding,
        limit=5,
        with_vectors=True,
    )
    context = get_context(search_results=search_results)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context_prompt.format(context=context)},
        {"role": "user", "content": query_prompt.format(query=query)},
    ]
    response = get_answer(
        model=config["openai"]["gpt_model"]["name"],
        temperature=config["openai"]["gpt_model"]["temperature"],
        messages=messages,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    print(request("Na koliko dana godisnjeg imam pravo kao zaposleni?"))
