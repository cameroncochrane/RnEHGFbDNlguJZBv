Getting started
===============

This page covers everything needed to go from a clean clone of the repo to a running app.

## 1. Prerequisites

- Python 3.12 (the project is pinned to `~=3.12.0` in `pyproject.toml`)
- `pip` (or `pipenv`, if you prefer — see `make create_environment`)

## 2. Set up the environment

From the project root:

```bash
# Create and activate a virtual environment (any method works, e.g.:)
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

# Install the base requirements + the project package itself
make requirements
```

`make requirements` installs everything listed in `requirements.txt` (`loguru`, `mkdocs`, `python-dotenv`, `ruff`, `tqdm`, `typer`) and installs `potential_talents_nlp` itself in editable mode (`pip install -e .`).

!!! note "A few extra packages aren't in requirements.txt yet"
    The Streamlit app and the recommender logic also depend on `streamlit`, `pandas`, `numpy`, and `scikit-learn`, and the notebook additionally uses `sentence-transformers` for its model comparison. Install these too:

    ```bash
    pip install streamlit pandas numpy scikit-learn sentence-transformers
    ```

## 3. Data

The candidate dataset already lives at:

```
data/raw/potential-talents - Aspiring human resources - seeking human resources.csv
```

It has four columns: `id`, `job_title`, `location`, `connection` (plus a `fit` column that the app drops on load, since it isn't used for ranking). No download or sync step is required — the app reads this file directly via `config.RAW_DATA_DIR`.

If you want to use your own candidate data, replace this CSV (or point `recommender.load_data()` at a different path) with a file that has at least `job_title`, `location`, and `connection` columns.

## 4. Environment variables (optional)

`potential_talents_nlp/config.py` loads a `.env` file from the project root if one exists (via `python-dotenv`). This isn't required to run the app today, but is there if you need to add API keys or other secrets later. **Never commit a real `.env` file to the repo.**

## 5. Run the Streamlit app

```bash
cd potential_talents_nlp
streamlit run app.py
```

This opens the Talent Recommender in your browser at `http://localhost:8501`. See [Usage](usage.md) for how to use it.

## 6. Explore the notebook

The exploratory work — including the comparison between TF-IDF and SentenceTransformers — lives in:

```
notebooks/PotentialTalents_1.ipynb
```

Open it with Jupyter (`jupyter lab` or `jupyter notebook`) once your environment is active.

## 7. Linting and formatting

```bash
make lint    # check style with ruff
make format  # auto-fix and format with ruff
```

## 8. Building the docs site

This documentation is a standard [MkDocs](https://www.mkdocs.org/) project, from the `docs/` folder:

```bash
cd docs
mkdocs build   # build the static site
mkdocs serve   # preview it locally with live reload
```
