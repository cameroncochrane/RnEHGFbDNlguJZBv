# Place cuustom modules such as the TF-IDF vectorizer and cosine similarity calculator here:

from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Direct to where the base csv is located:
from config import RAW_DATA_DIR

BASE_DATA_PATH = RAW_DATA_DIR / "potential-talents - Aspiring human resources - seeking human resources.csv"

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
    
    # Modify the base dataset by creating a 'combined' features column (to be used by the TF-IDF vectorizer).
    # Modified dataset will be in its own 'hidden' df i.e. not to be displayed:

    mod_df = df
    mod_df["combined"] = (mod_df["job_title"].astype(str)+ " located in " + mod_df["location"].astype(str) + ", with " + mod_df["connection"].astype(str)+ " connections.")
    # mod_df["combined"] is what will undergo tokenization + vectorization

    return df, mod_df


def rank_candidates(df: pd.DataFrame,query: str, top_n: int | None = None,) -> pd.DataFrame:
    """
    Rank all candidates in *df* by TF-IDF cosine similarity to *query*.

    Returns df with a new 'similarity_score' column, sorted descending.
    """
    if df.empty or not query.strip():
        df = df.copy()
        df["similarity_score"] = 0.0
        return df

    corpus = df["combined"].fillna("").tolist()
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words="english",
        min_df=1,
    )
    # Fit on corpus + query together so the query vocab is represented
    all_docs = corpus + [query]
    tfidf_matrix = vectorizer.fit_transform(all_docs)

    query_vec = tfidf_matrix[-1]          # last row = the query
    candidate_matrix = tfidf_matrix[:-1]  # all other rows

    scores = cosine_similarity(query_vec, candidate_matrix).flatten()

    result = df.copy()
    result["similarity_score"] = scores
    result = result.sort_values("similarity_score", ascending=False)

    if top_n:
        result = result.head(top_n)

    return result.reset_index(drop=True)


def rank_by_starred(df: pd.DataFrame, candidate_id: int, top_n: int | None = None) -> pd.DataFrame:
    """
    Use a starred candidate's 'combined' as the query.
    """

    row = df[df["id"] == candidate_id]
    if row.empty:
        raise ValueError(f"Candidate id={candidate_id} not found.")
    query = row.iloc[0]["combined"]
    # Exclude the starred candidate from results
    pool = df[df["id"] != candidate_id].copy()
    return rank_candidates(pool, query, top_n=top_n)

def rank_by_description(df: pd.DataFrame, description: str, top_n: int | None = None) -> pd.DataFrame:
    """
    Use a starred candidate's 'combined' as the query.
    """
    return rank_candidates(df, description, top_n)