from pathlib import Path

import panel as pn
import yaml

from database.utils import embed_text, get_context, search
from llm.prompts import CONTEXT_PROMPT, CONVERSATION_PROMPT, QUERY_PROMPT, SYSTEM_PROMPT
from llm.utils import get_answer

config_path = Path("./config.yaml")

with config_path.open("r") as file:
    config = yaml.safe_load(file)

pn.extension()

state = {"conversation": []}


async def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    state["conversation"].append({"role": "user", "content": contents})

    embedding_response = embed_text(
        text=contents, model=config["openai"]["embedding_model"]["name"]
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
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": CONVERSATION_PROMPT.format(conversation=state["conversation"]),
        },
        {"role": "user", "content": CONTEXT_PROMPT.format(context=context)},
        {"role": "user", "content": QUERY_PROMPT.format(query=contents)},
    ]
    response = get_answer(
        model=config["openai"]["gpt_model"]["name"],
        temperature=config["openai"]["gpt_model"]["temperature"],
        messages=messages,
        stream=True,
    )

    message = ""
    for chunk in response:
        part = chunk.choices[0].delta.content
        if part is not None:
            message += part
        yield message

    state["conversation"].append({"role": "assistant", "content": message})


if __name__ == "__main__":
    chat_interface = pn.chat.ChatInterface(
        callback=callback, callback_user="Law Assistant"
    )
    chat_interface.send(
        "Postavi pitanje iz radnog prava!", user="System", respond=False
    )
    chat_interface.servable()
