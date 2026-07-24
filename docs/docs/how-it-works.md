How It Works
============

## The pipeline

The recommender logic lives in `potential_talents_nlp/recommender.py` (at the project root). It works in three steps:

1. **Load & clean** (`load_data`) — read the raw CSV, drop the unused `fit` column, remove duplicate rows (same job title + location + connections), and re-number `id` so it's contiguous. No further feature engineering is needed — only the `job_title` column is used for similarity, so the 'viewable' and 'NLP-ready' frames are the same data.

2. **Embed with BERT** (`embed_texts`) — each candidate's `job_title` is tokenized and passed through `bert-base-uncased` (via `transformers`). The token embeddings from BERT's last hidden state are mean-pooled into a single vector per text, using the attention mask so padding tokens don't skew the average. The tokenizer/model are loaded once per process (`lru_cache`) since loading the weights is the expensive part.

3. **Rank by cosine similarity** (`rank_candidates`) — the query (embedded the same way) is compared against every candidate vector with `cosine_similarity`, producing a `similarity_score` between 0 and 1. Results are sorted descending and truncated to `top_n`.

Two entry points wrap this shared logic:

- `rank_by_starred(df, candidate_id, top_n)` — uses an existing candidate's `job_title` as the query, and excludes that candidate from the results.
- `rank_by_description(df, description, top_n)` — uses your typed text directly as the query.

Both are what power the two search modes described in [Usage](usage.md).

## Why BERT on `job_title`, and not TF-IDF or a combined-text column?

The notebooks work through several rounds of experimentation before landing on this approach:

- **`PotentialTalents_1.ipynb`** compares TF-IDF against `SentenceTransformers` embeddings over a combined `"{job_title} located in {location}, with {connection} connections."` string. Both struggled with ambiguous keywords — *"experienced"* or *"aspiring"* scored highly on their own, regardless of what the candidate was experienced *in* or aspiring *to*.
- **`PotentialTalents_2.ipynb`** tries several *static* embedding methods (Bag-of-Words, Word2Vec, GloVe, FastText) over the same combined text — none meaningfully improved on TF-IDF, since a fixed vector per word still can't distinguish "experienced in HR" from "experienced in something else." It then tries raw `bert-base-uncased` — a *contextual* model — first on the combined text, then on `job_title` alone. Dropping the boilerplate location/connections phrasing and keeping only `job_title` produced a clear improvement, since the repeated "located in X, with Y connections" text was diluting the signal shared across nearly every candidate.
- **`PotentialTalents_3.ipynb`** tries an SBERT first-pass + CrossEncoder rerank (two-stage retrieval), and re-compares SentenceTransformers and TF-IDF on both `job_title` and the combined text. The conclusion across all three notebooks: **BERT embeddings of `job_title` alone** gave the most precise, trustworthy rankings for this dataset, so that's what the Streamlit app uses in production — no `combined` column is created or used.

None of the approaches fully resolve the "aspiring" vs "experienced" semantic distinction — it remains the main known limitation.

**Practical implication:** when writing a role description to search against, being specific (e.g. *"aspiring HR professional with a business degree"* rather than just *"aspiring professional"*) will get better results.

## Extending this

If you want to try a different model or ranking strategy, `recommender.py` is a natural place to add a parallel function (e.g. `rank_by_cross_encoder`) following the same `(df, query, top_n) -> pd.DataFrame` shape as `rank_candidates`, so it can be wired into `app.py` alongside the existing modes.
