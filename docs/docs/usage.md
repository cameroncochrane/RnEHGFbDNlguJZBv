Usage
=====

Once the app is running (`streamlit run app.py` from `potential_talents_nlp/`), you'll see the **Talent Recommender** with two tabs: **Browse All** and **Find Candidates**.

## Browse All

A read-only table of every candidate currently in the dataset, showing:

- **ID** — the candidate's row identifier
- **Job Title**
- **Location**
- **Connections**

Use this to get a feel for the pool before searching, or to find the ID of a candidate you want to star.

## Find Candidates

This tab has two independent ways to rank candidates, side by side.

### Option A — Star a Candidate

1. Pick a candidate from the **Select candidate** dropdown (shown as `#<id> — <job title>`).
2. Adjust **Show top N results** (5–50) to control how many ranked results come back.
3. Click **⭐ Rank by this candidate**.

The app builds a query from the starred candidate's combined text (job title + location + connections) and ranks every *other* candidate in the pool by cosine similarity to it — i.e. "find people like this person." The starred candidate itself is excluded from the results.

### Option B — Describe your ideal candidate

1. Type a free-text description into **Role description**, e.g. *"a graduate with an interest in HR"*.
2. Adjust **Show top N results** (5–50).
3. Click **Find matching candidates**.

The description is vectorized the same way as candidate text and used directly as the similarity query — no need to pick an existing candidate first.

### Reading the results

Whichever option you use, the results section below shows:

- A **ranked table** with `id`, `job_title`, `connection`, `location`, and `similarity_score` (0–1, higher is more similar).
- A **Score distribution** chart (expand it to view) — a bar chart of `similarity_score` per candidate, useful for spotting whether the top results are clearly ahead of the pack or all bunched together.

If a query returns no results (e.g. an empty description), you'll see an on-screen message asking you to try a different query.

## Tips

- Very short or generic descriptions (e.g. just "experienced") tend to match too broadly — see [How It Works](how-it-works.md) for why, and try to include specifics like role, seniority, or location.
- Starring a candidate is a quick way to source "more like this" without writing a description from scratch.
