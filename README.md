# Legal ChatBot Documentation

## Setting Up the Project

### Step 1: Installing Poetry
We use Poetry for dependency management. First, check if Poetry is installed by running:
```bash
poetry -V
```

If it shows a version like Poetry (version x.y.z), you're set. If not, follow the [official guidelines](https://python-poetry.org/docs/) to install Poetry.

> 📎 _**Note**: Though a requirements.txt is provided, Poetry is recommended for efficient dependency management._

### Step 2: Environment Setup
Configuring Poetry

To maintain organization, configure Poetry to create a virtual environment in the project's directory:
```bash
poetry config virtualenvs.in-project true
```

### Step 3: Installing Dependencies
Install all the project's dependencies with:
```bash
poetry install --no-root
```
> 📎 _**Note**: Use the `--no-root` option to skip installing the project package itself._

### Step 4: Activating the Virtual Environment
Post-installation, activate the virtual environment located in the `.venv` directory.

For macOS/Linux:
```bash
source .venv/bin/activate
```
For Windows:
```bash
.venv\Scripts\activate
```

### Step 5: Initializing Qdrant:

Qdrant is a sophisticated vector database and vector similarity search engine that operates as an API service. It allows for the searching of nearest high-dimensional vectors, transforming embeddings or neural network encoders into comprehensive applications suitable for matching, searching, recommending, among other functionalities.

For setup, you will require two crucial pieces of information: **QDRANT_CLUSTER_URL** and **QDRANT_API_KEY**.

To begin, create a free account with Qdrant by signing up [here](https://cloud.qdrant.io/login). Following account creation, proceed to set up a cluster for your vector database; this is where you'll obtain your **QDRANT_CLUSTER_URL**. Lastly, generate your **QDRANT_API_KEY** by navigating to the "Data Access Control" section within your Qdrant dashboard.

### Step 6: Environment variables:
For the project to work you need to create a `.env` file in the project root.

The file should look like this:
```yml
QDRANT_CLUSTER_URL=ADD_YOUR_QDRANT_CLUSTER_URL
QDRANT_API_KEY=ADD_YOUR_QDRANT_API_KEY

OPENAI_API_KEY=ADD_YOUR_OPENAI_API_KEY
```

## Run the Demo:
You can run the demo locally simply by executing this command in your terminal:
```bash
streamlit run app.py  
```
And UI will be available in your browser on the URL:
```
http://localhost:8501
```
