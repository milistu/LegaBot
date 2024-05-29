# Router Module

This directory contains scripts and utilities for routing user queries to the appropriate legal documents.

## Overview

- `query_router.py`: Main script for routing semantic queries to the appropriate collections using OpenAI's API.
- `router_prompt.py`: Contains the prompt template used to determine relevant laws based on user queries.

## Setup

Refer to the main README for details on setting up the environment and dependencies using Poetry.

### Environment Configuration

Before running the scripts, ensure you have set the necessary environment variables in your `.env` file:
```yaml
OPENAI_API_KEY=
```

## Scripts

- `query_router.py` - This script routes a semantic query to the appropriate collections using OpenAI's API.
- `router_prompt.py` - This script contains the prompt template used to determine relevant laws based on user queries.

## Usage

To route a query and get the relevant laws, use the **semantic_query_router** function from `query_router.py`. Make sure to format your query and prompt correctly and provide the required API key in the .env file.

```python
from openai import OpenAI
from router.query_router import semantic_query_router
from router.router_prompt import ROUTER_PROMPT

client = OpenAI(api_key='YOUR_OPENAI_API_KEY')

query = "What are the conditions for terminating an employment contract?"
response = semantic_query_router(client, query, ROUTER_PROMP)
print(response)
```