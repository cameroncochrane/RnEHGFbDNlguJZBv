# RnEHGFbDNlguJZBv documentation!

## Description

An NLP project implemented in Python for an HR solutions platform — a **Talent Recommender** that ranks job candidates by relevance, using text similarity rather than manual keyword filtering.

Recruiters can:

- **Browse** every candidate in the dataset in one searchable table.
- **Star an existing candidate** and instantly see who else in the pool looks most similar to them.
- **Type a description of the ideal hire** (e.g. *"an experienced HR professional in New York"*) and get a ranked shortlist.

Under the hood, each candidate's job title is embedded with a **BERT** (`bert-base-uncased`) transformer model and compared using cosine similarity. See [How It Works](how-it-works.md) for the details, and [Usage](usage.md) for a guided tour of the app itself.

## Where to go next

| Page | What's in it |
|---|---|
| [Getting Started](getting-started.md) | Environment setup, installing dependencies, running the app and the notebooks |
| [Usage](usage.md) | Walkthrough of the Streamlit UI — browsing, starring, and description search |
| [How It Works](how-it-works.md) | The BERT + cosine similarity pipeline, and the comparison against TF-IDF, Bag-of-Words, Word2Vec, GloVe, FastText, and SentenceTransformers from the notebooks |

## Commands

The `Makefile` contains the central entry points for common tasks related to this project:

| Command | Effect |
|---|---|
| `make requirements` | Upgrade pip and install everything in `requirements.txt` |
| `make lint` | Check code style and formatting with `ruff` |
| `make format` | Auto-fix and format code with `ruff` |
| `make clean` | Remove compiled Python files and `__pycache__` directories |
| `make create_environment` | Create a `pipenv` environment for the project |
