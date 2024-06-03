from typing import Dict, List

from router.router_prompt import ROUTER_PROMPT, USER_QUERY


def formate_messages_router(
    query: str,
) -> List[Dict]:
    """
    Prepare the list of messages for the llm model.

    Args:
        query (str): The user's query.

    Returns:
        List[Dict]: The list of messages formatted for the llm model.
    """
    return [
        {"role": "system", "content": ROUTER_PROMPT},
        {"role": "user", "content": USER_QUERY.format(query=query)},
    ]
