import json
from pathlib import Path

import streamlit as st
import yaml
from loguru import logger

from database.utils import embed_text, get_context, search
from llm.prompts import INTRODUCTION_MESSAGE
from llm.utils import get_answer, get_messages
from router.query_router import rout_query

st.title("Legal ChatBot")


config_path = Path("./config.yaml")
centroid_path = Path("./router/collection_centroids.json")

with config_path.open("r") as file:
    config = yaml.safe_load(file)

with open(centroid_path, "r", encoding="utf-8") as file:
    centroids = json.loads(file.read())


def response_generator(query: str):
    st.session_state.messages = st.session_state.messages[
        -1 * config["openai"]["gpt_model"]["max_conversation"] :
    ]

    # st.session_state.messages.append({"role": "user", "content": query})

    embedding_response = embed_text(
        text=query, model=config["openai"]["embedding_model"]["name"]
    )
    embedding = embedding_response.data[0].embedding

    # Add query
    collection_name = rout_query(
        centroids=centroids, query_embedding=embedding
    ).replace("-", "_")
    logger.info(f"Query routed to collection name: {collection_name}")

    search_results = search(
        collection=collection_name,
        query_vector=embedding,
        limit=10,
        with_vectors=True,
    )
    context = get_context(search_results=search_results)

    stream = get_answer(
        model=config["openai"]["gpt_model"]["name"],
        temperature=config["openai"]["gpt_model"]["temperature"],
        messages=get_messages(
            context=context, query=query, conversation=st.session_state.messages
        ),
        stream=True,
    )

    for chunk in stream:
        part = chunk.choices[0].delta.content
        if part is not None:
            yield part


if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": INTRODUCTION_MESSAGE}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if prompt := st.chat_input("Postavi pitanje iz prava..."):
    # Generate and display the response
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = response_generator(prompt)
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
