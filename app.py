import streamlit as st
from dotenv import find_dotenv, load_dotenv

from llm.prompts import INTRODUCTION_MESSAGE
from utils import (
    generate_response,
    init_clients,
    load_config_from_yaml,
    WARNING_MESSAGE,
    QUERY_SUGGESTIONS,
    AUTHORS,
    LOGO_URL,
)

# Load environment variables.
load_dotenv(find_dotenv())


# Configure Streamlit page
st.set_page_config(page_title="Your Lawyer Assistant", page_icon=LOGO_URL)

st.title("LegaBot")
st.divider()

st.logo(LOGO_URL, icon_image=LOGO_URL)
with st.sidebar:
    st.subheader("💡 Query Suggestions")
    with st.container(border=True, height=200):
        st.markdown(QUERY_SUGGESTIONS)
    st.subheader("⚠️ Warning")
    with st.container(border=True):
        st.markdown(WARNING_MESSAGE)
    st.subheader("✍️ Authors")
    with st.container(border=True):
        st.markdown(AUTHORS)

openai_client, qdrant_client = init_clients()
config = load_config_from_yaml()


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
        stream = generate_response(
            query=prompt,
            openai_client=openai_client,
            qdrant_client=qdrant_client,
            config=config,
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
