from typing import Dict, List

from langfuse.decorators import observe
from openai import OpenAI
from openai.types.chat import ChatCompletion

from llm.prompts import (
    CONTEXT_PROMPT,
    CONVERSATION_PROMPT,
    QUERY_PROMPT,
    SYSTEM_PROMPT,
)


@observe()
def get_answer(
    client: OpenAI,
    model: str,
    temperature: float,
    messages: List[Dict],
    stream: bool = False,
) -> ChatCompletion:
    """
    Get an answer from the OpenAI chat model.

    Args:
        client (OpenAI): The OpenAI client instance.
        model (str): The model name to use.
        temperature (float): The temperature setting for the model.
        messages (List[Dict]): The list of messages to send to the model.
        stream (bool, optional): Whether to stream the response. Defaults to False.

    Returns:
        ChatCompletion: The chat completion response from OpenAI.
    """
    return client.chat.completions.create(
        model=model, temperature=temperature, messages=messages, stream=stream
    )


def get_messages(context: str, query: str, conversation: List[str]) -> List[Dict]:
    """
    Prepare the list of messages for the chat model.

    Args:
        context (str): The context information.
        query (str): The user's query.
        conversation (List[str]): The conversation history.

    Returns:
        List[Dict]: The list of messages formatted for the chat model.
    """
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": CONVERSATION_PROMPT.format(conversation=conversation),
        },
        {"role": "user", "content": CONTEXT_PROMPT.format(context=context)},
        {"role": "user", "content": QUERY_PROMPT.format(query=query)},
    ]
