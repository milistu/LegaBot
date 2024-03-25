import os
from pathlib import Path

import yaml
from openai import OpenAI
from openai.types.chat import ChatCompletion

config_path = Path("./config.yaml")
with config_path.open("r") as file:
    config = yaml.safe_load(file)

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
)


def get_answer(
    model: str, temperature: float, messages: list, stream: bool = False
) -> ChatCompletion:
    response = client.chat.completions.create(
        model=model, temperature=temperature, messages=messages, stream=stream
    )

    return response
