# Place custom modules such as the BERT embedder and cosine similarity calculator here:

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModel, AutoTokenizer

# Direct to where the base csv is located:
from config import RAW_DATA_DIR

BASE_DATA_PATH = RAW_DATA_DIR / "potential-talents - Aspiring human resources - seeking human resources.csv"

BERT_MODEL_NAME = "bert-base-uncased"


# Data loading and pre-processing:
def load_data(data_path: str | Path = BASE_DATA_PATH) -> pd.DataFrame:
    "Load the base dataset from a CSV file to a pd.DataFrame and return the viewable df and modified df ready for NLP"

    # Import the base dataset, remove the 'fit' column and return. This is the 'visible' df
    if data_path is not None:
        df = pd.read_csv(data_path)
    else:
        raise ValueError("No dataset path is provided. Provide one")

    if "fit" in df.columns:
        df = df.drop(columns=["fit"])

    # Remove the duplicates and 'reset' the id column to account for dropped rows:
    df = df.drop_duplicates(subset=["job_title", "location", "connection"]).reset_index(drop=True) #All id's are unique, but the info in the other columns (when combined), aren't
    df["id"] = df.index + 1

    # No further feature engineering needed: BERT embeds "job_title" directly, so the
    # 'viewable' and 'NLP-ready' frames are the same data.
    return df, df.copy()


@lru_cache(maxsize=1)
def _get_bert():
    "Load and cache the BERT tokenizer/model so weights are only loaded once per process."
    tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL_NAME)
    model = AutoModel.from_pretrained(BERT_MODEL_NAME)
    model.eval()
    return tokenizer, model


def embed_texts(texts: list[str]) -> np.ndarray:
    "Mean-pool BERT token embeddings (attention-mask aware) into one vector per text."
    tokenizer, model = _get_bert()
    inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)

    token_embeddings = outputs.last_hidden_state
    mask = inputs["attention_mask"].unsqueeze(-1).float()
    summed = (token_embeddings * mask).sum(dim=1)
    counts = mask.sum(dim=1).clamp(min=1e-9)
    return (summed / counts).numpy()


def rank_candidates(df: pd.DataFrame, query: str, top_n: int | None = None) -> pd.DataFrame:
    """
    Rank all candidates in *df* by BERT cosine similarity to *query*, embedding each
    candidate's 'job_title'.

    Returns df with a new 'similarity_score' column, sorted descending.
    """
    if df.empty or not query.strip():
        df = df.copy()
        df["similarity_score"] = 0.0
        return df

    corpus = df["job_title"].fillna("").tolist()
    candidate_vecs = embed_texts(corpus)
    query_vec = embed_texts([query])

    scores = cosine_similarity(query_vec, candidate_vecs).flatten()

    result = df.copy()
    result["similarity_score"] = scores
    result = result.sort_values("similarity_score", ascending=False)

    if top_n:
        result = result.head(top_n)

    return result.reset_index(drop=True)


def rank_by_starred(df: pd.DataFrame, candidate_id: int, top_n: int | None = None) -> pd.DataFrame:
    """
    Use a starred candidate's 'job_title' as the query.
    """

    row = df[df["id"] == candidate_id]
    if row.empty:
        raise ValueError(f"Candidate id={candidate_id} not found.")
    query = row.iloc[0]["job_title"]
    # Exclude the starred candidate from results
    pool = df[df["id"] != candidate_id].copy()
    return rank_candidates(pool, query, top_n=top_n)

def rank_by_description(df: pd.DataFrame, description: str, top_n: int | None = None) -> pd.DataFrame:
    """
    Use a free-text role description as the query.
    """
    return rank_candidates(df, description, top_n)
