# HR Talent Recommender - An NLP Approach

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

**An NLP-powered talent recommender for HR sourcing.** Given a pool of candidate profiles (job title, location, connections), the app ranks them by relevance to either an existing "starred" candidate or a free-text description of the role you're hiring for — using **BERT** (`bert-base-uncased`) embeddings of each candidate's job title and cosine similarity.

📖 Full documentation lives in [`docs/`](docs/docs/index.md) (built with [MkDocs](https://www.mkdocs.org/)). This README is a quick-start summary.

## What it does

Recruiters often have a shortlist of candidates and want to know: *"who else in my database looks like this person?"* or *"who best matches this role description?"* This project answers both questions:

- **Browse** the full candidate list in a searchable table.
- **Star a candidate** you already like, and rank everyone else in the pool by similarity to them.
- **Describe your ideal hire** in plain text (e.g. *"a graduate with an interest in HR"*), and rank candidates against that description.

Results are scored with a `similarity_score` (0–1) and shown as a ranked table plus a bar chart of the score distribution.

## Quick start

```bash
# 1. Clone and enter the project
git clone <this-repo>
cd RnEHGFbDNlguJZBv

# 2. Create an environment and install dependencies
make requirements
# this installs everything in requirements.txt, plus the project itself (`pip install -e .`)

# 3. The app also needs a few libraries not pinned in requirements.txt — install them too:
pip install streamlit pandas numpy scikit-learn transformers torch

# 4. Launch the Streamlit app
cd potential_talents_nlp
streamlit run app.py
```

Streamlit will open the app in your browser (usually `http://localhost:8501`). See [Getting Started](docs/docs/getting-started.md) for a more detailed walkthrough and [Usage](docs/docs/usage.md) for how to drive the UI.

## How it works (short version)

1. Each candidate's `job_title` text is fed through **BERT** (`bert-base-uncased`, via `transformers`).
2. Token embeddings from BERT's last hidden state are mean-pooled (attention-mask aware) into a single vector per job title.
3. The query (either a starred candidate's job title, or your typed description) is embedded the same way.
4. **Cosine similarity** between the query and every candidate produces the `similarity_score` used to rank results.

The project's notebooks ([`PotentialTalents_1.ipynb`](notebooks/PotentialTalents_1.ipynb), [`PotentialTalents_2.ipynb`](notebooks/PotentialTalents_2.ipynb), [`PotentialTalents_3.ipynb`](notebooks/PotentialTalents_3.ipynb)) compare TF-IDF, Bag-of-Words, Word2Vec, GloVe, FastText, SentenceTransformers, and BERT — see [How It Works](docs/docs/how-it-works.md) for the comparison and why BERT on `job_title` was kept as the production approach.

## Project Organization

```
├── LICENSE            <- Open-source license (MIT)
├── Makefile           <- Convenience commands: `make requirements`, `make lint`, `make format`, `make clean`
├── README.md          <- You are here
├── data
│   ├── external       <- Data from third party sources (currently empty)
│   ├── interim        <- Intermediate data that has been transformed (currently empty)
│   ├── processed      <- The final, canonical data sets for modeling (currently empty)
│   └── raw            <- The original candidate CSV: `potential-talents - ... .csv`
│
├── docs               <- MkDocs project — build with `mkdocs build`, preview with `mkdocs serve`
│   ├── docs
│   │   ├── index.md            <- Docs home / project overview
│   │   ├── getting-started.md  <- Installation & running instructions
│   │   ├── usage.md            <- How to use the Streamlit app
│   │   └── how-it-works.md     <- BERT / cosine similarity methodology
│   └── mkdocs.yml     <- MkDocs site configuration
│
├── models             <- Trained/serialized models (currently unused — the recommender is computed on the fly)
│
├── notebooks
│   ├── PotentialTalents_1.ipynb  <- Exploratory analysis, TF-IDF vs SentenceTransformers comparison
│   ├── PotentialTalents_2.ipynb  <- Bag-of-Words, Word2Vec, GloVe, FastText, and BERT comparison
│   └── PotentialTalents_3.ipynb  <- SBERT + CrossEncoder rerank vs BERT vs TF-IDF, job_title vs combined text
│
├── pyproject.toml     <- Package metadata for `potential_talents_nlp` + ruff (lint/format) config
│
├── references         <- Data dictionaries, manuals, and other explanatory materials
│
├── reports
│   └── figures        <- Generated graphics and figures for reporting
│
├── requirements.txt   <- Base dependency list (see note in Getting Started about extra packages needed)
│
└── potential_talents_nlp   <- Source code for the app
    ├── __init__.py         <- Makes potential_talents_nlp a Python module
    ├── config.py           <- Central path config (data dirs, models dir, .env loading)
    ├── recommender.py      <- Data loading, BERT embedding, cosine similarity ranking
    └── app.py              <- Streamlit front end
```

--------
