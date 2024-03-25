from pathlib import Path

import yaml
from taipy.gui import Gui, State, notify

from llm.prompts import QUERY_PROMPT, CONTEXT_PROMPT, CONVERSATION_PROMPT, SYSTEM_PROMPT
from llm.utils import get_answer
from database.utils import embed_text, search, get_context

config_path = Path("./config.yaml")

with config_path.open("r") as file:
    config = yaml.safe_load(file)

client = None
conversation = {
    "Conversation": [],
}
current_user_message = ""
past_conversations = []
selected_conv = None
selected_row = [1]


def on_init(state: State) -> None:
    """
    Initialize the app.

    Args:
        - state: The current state of the app.
    """
    state.conversation = conversation
    state.current_user_message = current_user_message
    state.past_conversations = past_conversations
    state.selected_conv = selected_conv
    state.selected_row = selected_row


def request(state: State, query: str) -> str:
    """
    Send a prompt to the GPT API and return the response.

    Args:
        - state: The current state.
        - query: The query to send to the API.

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
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": CONVERSATION_PROMPT.format(conversation=state.conversation),
        },
        {"role": "user", "content": CONTEXT_PROMPT.format(context=context)},
        {"role": "user", "content": QUERY_PROMPT.format(query=query)},
    ]
    response = get_answer(
        model=config["openai"]["gpt_model"]["name"],
        temperature=config["openai"]["gpt_model"]["temperature"],
        messages=messages,
    )

    return response.choices[0].message.content


# def update_context(state: State) -> None:
#     """
#     Update the `conversation` with the user's message and the AI's response.

#     Args:
#         - state: The current state of the app.
#     """
#     temp_conv = f"Čovek: \n {state.current_user_message}\n\n Asistent: \n "
#     answer = request(state, state.current_user_message).replace("\n", "")
#     temp_conv += answer
#     state.selected_row = [len(state.conversation["Conversation"]) + 1]
#     return answer


def send_message(state: State) -> None:
    """
    Send the user's message to the API and update the conversation.

    Args:
        - state: The current state of the app.
    """
    notify(state, "info", "Sending message...")
    answer = request(state, state.current_user_message).replace("\n", "")
    state.selected_row = [len(state.conversation["Conversation"]) + 1]

    conv = state.conversation._dict.copy()
    conv["Conversation"] += [state.current_user_message, answer]
    state.current_user_message = ""
    state.conversation = conv
    notify(state, "success", "Response received!")


def style_conv(state: State, idx: int, row: int) -> str:
    """
    Apply a style to the conversation table depending on the message's author.

    Args:
        - state: The current state of the app.
        - idx: The index of the message in the table.
        - row: The row of the message in the table.

    Returns:
        The style to apply to the message.
    """
    if idx is None:
        return None
    elif idx % 2 == 0:
        return "user_message"
    else:
        return "gpt_message"


def on_exception(state, function_name: str, ex: Exception) -> None:
    """
    Catches exceptions and notifies user in Taipy GUI

    Args:
        state (State): Taipy GUI state
        function_name (str): Name of function where exception occured
        ex (Exception): Exception
    """
    notify(state, "error", f"An error occured in {function_name}: {ex}")


def reset_chat(state: State) -> None:
    """
    Reset the chat by clearing the conversation.

    Args:
        - state: The current state of the app.
    """
    state.past_conversations = state.past_conversations + [
        [len(state.past_conversations), state.conversation]
    ]
    state.conversation = {
        "Conversation": [
            "Ko si ti?",
            "Pozdra, ja sam AI Pravni Asistent. Kako Vam mogu pomoći?",
        ]
    }


def tree_adapter(item: list) -> [str, str]:
    """
    Converts element of past_conversations to id and displayed string

    Args:
        item: element of past_conversations

    Returns:
        id and displayed string
    """
    identifier = item[0]
    if len(item[1]["Conversation"]) > 3:
        return (identifier, item[1]["Conversation"][2][:50] + "...")
    return (item[0], "Empty conversation")


def select_conv(state: State, var_name: str, value: list) -> None:
    """
    Selects conversation from past_conversations

    Args:
        state: The current state of the app.
        var_name: "selected_conv"
        value: [[id, conversation]]
    """
    state.conversation = state.past_conversations[value[0][0]][1]
    state.selected_row = [len(state.conversation["Conversation"]) + 1]


past_prompts = []

page = """
<|layout|columns=300px 1|
<|part|class_name=sidebar|
# Law **ChatBot**{: .color-primary} # {: .logo-text}
<|New Conversation|button|class_name=fullwidth plain|id=reset_app_button|on_action=reset_chat|>
### Previous activities ### {: .h5 .mt2 .mb-half}
<|{selected_conv}|tree|lov={past_conversations}|class_name=past_prompts_list|multiple|adapter=tree_adapter|on_change=select_conv|>
|>

<|part|class_name=p2 align-item-bottom table|
<|{conversation}|table|style=style_conv|show_all|selected={selected_row}|rebuild|>
<|part|class_name=card mt1|
<|{current_user_message}|input|label=Write your message here...|on_action=send_message|class_name=fullwidth|change_delay=-1|>
|>
|>
|>
"""


if __name__ == "__main__":
    Gui(page).run(
        debug=True,
        dark_mode=True,
        use_reloader=True,
        title="👩‍⚖️ Law ChatBot",
        port=8080,
    )
