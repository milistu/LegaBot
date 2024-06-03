from typing import Dict, List

from llm.prompts import (
    CONTEXT_PROMPT,
    CONVERSATION_PROMPT,
    QUERY_PROMPT,
    SYSTEM_PROMPT,
)


def formate_messages_chat(
    context: str, query: str, conversation: List[str]
) -> List[Dict]:
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
