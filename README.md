# Law ChatBot Documentation

## Setting Up the Project

### Step 1: Installing Poetry
We use Poetry for dependency management. First, check if Poetry is installed by running:
```bash
poetry -V
```

If it shows a version like Poetry (version x.y.z), you're set. If not, follow the [official guidelines](https://python-poetry.org/docs/) to install Poetry.

_**Note**: Though a requirements.txt is provided, Poetry is recommended for efficient dependency management._

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
_**Note**: Use the `--no-root` option to skip installing the project package itself._

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