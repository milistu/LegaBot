from pathlib import Path

import panel as pn
import yaml

from database.utils import embed_text, get_context, search
from llm.prompts import INTRODUCTION_MESSAGE
from llm.utils import get_answer, get_messages

config_path = Path("./config.yaml")

with config_path.open("r") as file:
    config = yaml.safe_load(file)

pn.extension()

state = {"conversation": []}


async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    state["conversation"] = state["conversation"][
        config["openai"]["gpt_model"]["max_conversation"] :
    ]

    state["conversation"].append({"role": "user", "content": contents})

    embedding_response = embed_text(
        text=contents, model=config["openai"]["embedding_model"]["name"]
    )
    embedding = embedding_response.data[0].embedding

    search_results = search(
        collection=config["collection"]["name"],
        query_vector=embedding,
        limit=10,
        with_vectors=True,
    )
    context = get_context(search_results=search_results)

    response = get_answer(
        model=config["openai"]["gpt_model"]["name"],
        temperature=config["openai"]["gpt_model"]["temperature"],
        messages=get_messages(
            context=context, query=contents, conversation=state["conversation"]
        ),
        stream=True,
    )

    message = ""
    for chunk in response:
        part = chunk.choices[0].delta.content
        if part is not None:
            message += part
        yield message

    state["conversation"].append({"role": "assistant", "content": message})


chat_interface = pn.chat.ChatInterface(callback=callback, callback_user="Law Assistant")
chat_interface.send(INTRODUCTION_MESSAGE, user="Law Assistant", respond=False)
chat_interface.servable()
