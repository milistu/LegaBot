from pathlib import Path
from typing import Dict, List

import yaml
from langfuse.decorators import observe
from openai import OpenAI
from openai.types.chat import ChatCompletion

from llm.prompts import (
    CONTEXT_PROMPT,
    CONVERSATION_PROMPT,
    QUERY_PROMPT,
    SYSTEM_PROMPT,
)

config_path = Path("./config.yaml")
with config_path.open("r") as file:
    config = yaml.safe_load(file)


@observe()
def get_answer(
    client: OpenAI, model: str, temperature: float, messages: list, stream: bool = False
) -> ChatCompletion:
    response = client.chat.completions.create(
        model=model, temperature=temperature, messages=messages, stream=stream
    )

    return response


def get_messages(context: str, query: str, conversation: List[str]) -> List[Dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": CONVERSATION_PROMPT.format(conversation=conversation),
        },
        {"role": "user", "content": CONTEXT_PROMPT.format(context=context)},
        {"role": "user", "content": QUERY_PROMPT.format(query=query)},
    ]
