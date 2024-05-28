import json
from typing import List

from langfuse.decorators import observe
from openai import OpenAI


@observe()
def semantic_query_router(
    client: OpenAI,
    query: str,
    prompt: str,
    temperature: float,
    model: str = "gpt-3.5-turbo",
) -> List[str]:
    """
    Routes a semantic query to the appropriate collections using OpenAI's API.

    Args:
        client (OpenAI): The OpenAI client instance.
        query (str): The query string to be routed.
        prompt (str): The prompt template to be used for the query.
        temperature (float): The temperature setting for the model's response.
        model (str, optional): The model to be used. Defaults to "gpt-3.5-turbo".

    Returns:
        List[str]: A list of collections that are relevant to the query.
    """
    # Create the completion request to the OpenAI API
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": prompt.format(query=query)}],
        temperature=temperature,
    )
    # Parse the response to extract the collections
    collections = json.loads(response.choices[0].message.content)["response"]
    return collections
