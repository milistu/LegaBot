import json
import os
from pathlib import Path

import streamlit as st
import yaml
from dotenv import find_dotenv, load_dotenv
from langfuse.decorators import observe
from loguru import logger
from openai import OpenAI
from qdrant_client import QdrantClient

from database.utils import embed_text, get_context, search
from llm.prompts import DEFAULT_CONTEXT, INTRODUCTION_MESSAGE
from llm.utils import get_answer, get_messages
from router.query_router import semantic_query_router
from router.router_prompt import DEFAULT_ROUTER_RESPONSE, ROUTER_PROMPT

load_dotenv(find_dotenv())

st.title("Legal ChatBot")

qdrant_client = QdrantClient(
    url=os.environ["QDRANT_CLUSTER_URL"],
    api_key=os.environ["QDRANT_API_KEY"],
)

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

config_path = Path("./config.yaml")
centroid_path = Path("./router/collection_centroids.json")

with config_path.open("r") as file:
    config = yaml.safe_load(file)

# Delete this
with open(centroid_path, "r", encoding="utf-8") as file:
    centroids = json.loads(file.read())


@observe()
def response_generator(query: str):
    st.session_state.messages = st.session_state.messages[
        -1 * config["openai"]["gpt_model"]["max_conversation"] :
    ]

    # st.session_state.messages.append({"role": "user", "content": query})

    embedding_response = embed_text(
        client=openai_client,
        text=query,
        model=config["openai"]["embedding_model"]["name"],
    )
    embedding = embedding_response.data[0].embedding

    # Rout query
    collections = semantic_query_router(
        client=openai_client,
        query=query,
        prompt=ROUTER_PROMPT,
        temperature=config["openai"]["gpt_model"]["temperature"],
    )
    logger.info(f"Query routed to collections: {collections}")

    if collections[0] == DEFAULT_ROUTER_RESPONSE:
        context = DEFAULT_CONTEXT
    else:
        search_results = []
        for collection_name in collections:
            search_results.extend(
                search(
                    client=qdrant_client,
                    collection=collection_name,
                    query_vector=embedding,
                    limit=10,
                    with_vectors=True,
                )
            )

        top_k = 15 if len(collections) > 1 else 10
        context = get_context(search_results=search_results, top_k=top_k)

    stream = get_answer(
        client=openai_client,
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
