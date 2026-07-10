How It Works
============

## The pipeline

The recommender logic lives in `potential_talents_nlp/recommender.py` (at the project root). It works in four steps:

1. **Load & clean** (`load_data`) — read the raw CSV, drop the unused `fit` column, remove duplicate rows (same job title + location + connections), and re-number `id` so it's contiguous.
2. **Combine features** — each candidate's `job_title`, `location`, and `connection` count are concatenated into one string, e.g.:

    ```
    "HR Coordinator located in Houston, Texas, with 85 connections."
    ```

    This `combined` text is what gets compared for similarity — it captures more signal than any single column alone.

3. **Vectorize with TF-IDF** (`rank_candidates`) — `scikit-learn`'s `TfidfVectorizer` turns the `combined` text of every candidate, *plus* the query text, into numeric vectors. Settings used:
    - `ngram_range=(1, 2)` — considers both single words and two-word phrases (so "human resources" is captured as a unit, not just "human" and "resources" separately).
    - `stop_words="english"` — filters out common words like "the", "and", "with".
    - The vectorizer is fit on the candidate corpus *and* the query together, so query-only vocabulary is represented too.

4. **Rank by cosine similarity** — the query vector is compared against every candidate vector with `cosine_similarity`, producing a `similarity_score` between 0 and 1. Results are sorted descending and truncated to `top_n`.

Two entry points wrap this shared logic:

- `rank_by_starred(df, candidate_id, top_n)` — uses an existing candidate's `combined` text as the query, and excludes that candidate from the results.
- `rank_by_description(df, description, top_n)` — uses your typed text directly as the query.

Both are what power the two search modes described in [Usage](usage.md).

## Why TF-IDF, not embeddings?

The notebook (`notebooks/PotentialTalents_1.ipynb` at the project root) tries a second approach — sentence embeddings via `sentence-transformers` — as a candidate replacement for TF-IDF, and compares the two side by side.

The finding: `SentenceTransformers` tended to give **high scores to candidates who didn't actually fit the target profile**, because both models struggled with the same ambiguous keywords — words like *"experienced"* or *"aspiring"* scored highly on their own, regardless of what the candidate was experienced *in* or aspiring *to*. On the test queries explored in the notebook, TF-IDF's simpler, more literal keyword/n-gram matching produced more precise, trustworthy rankings for this dataset — so it's what the Streamlit app uses in production.

**Practical implication:** when writing a role description to search against, being specific (e.g. *"aspiring HR professional with a business degree"* rather than just *"aspiring professional"*) will get better results, since the matching is fundamentally keyword/phrase-based rather than semantic.

## Extending this

If you want to revisit embeddings later, or add a new ranking strategy, `recommender.py` is a natural place to add a parallel function (e.g. `rank_by_embedding`) following the same `(df, query, top_n) -> pd.DataFrame` shape as `rank_candidates`, so it can be wired into `app.py` alongside the existing modes.
