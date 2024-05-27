# Database Module

This directory contains the scripts and utilities for processing and embedding scraped data and upserting it into a vector database.

## Overview

- `utils.py`: Utility functions for embedding text, managing collections in the Qdrant vector database, and handling data files.
- `vector_database.py`: **Main** script for creating embeddings from scraped data and storing them in a vector database.
- `api_request_parallel_processor.py`: Handles parallel API requests to the OpenAI API for text embedding, ensuring efficient usage of API rate limits.

## Setup

Refer to the main README for details on setting up the environment and dependencies using Poetry.

### Qdrant Setup
To use Qdrant for storing embeddings:

- Create a Free Cluster:

    Visit [Qdrant Cloud](https://cloud.qdrant.io/accounts/530e9933-88c7-42b7-a027-734ec6f5eb57/overview) and sign up for an account.
    Follow the prompts to create a new cluster. Select the free tier if available.

- Get API Key and Cluster URL:

    Once your cluster is ready, navigate to the dashboard.
    Find your cluster's URL and API key under the 'Settings' or 'API' section.

### Environment Configuration

Before running the scripts, ensure you have set the necessary environment variables in your `.env` file:
```yaml
QDRANT_CLUSTER_URL=
QDRANT_API_KEY=
OPENAI_API_KEY=
```

## Usage

To process and embed scraped data and upsert it to the vector database, use the following command from your project root:

```bash
python -m database.vector_database --scraped_dir ./scraper/test_laws/ --model text-embedding-3-small
```

This command will automatically handle all steps from data preparation, embedding, and upserting to the Qdrant vector database.
