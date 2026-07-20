# This is the master 'src' script for the Streamlit front end that will be run by the user.

# CCDS Imports:
from config import RAW_DATA_DIR

# Base Imports:
import streamlit as st

# Custom Imports:
from recommender import load_data, rank_by_description, rank_by_starred

BASE_DATA_PATH = RAW_DATA_DIR / "potential-talents - Aspiring human resources - seeking human resources.csv"
df, mod_df = load_data(BASE_DATA_PATH)

# Define base layout:
st.set_page_config(
    page_title="Talent Recommender",
    layout="wide",  # Makes the app much wider
    initial_sidebar_state="expanded",
)

# Add them to the session memory:
st.session_state.setdefault("df", df)
st.session_state.setdefault("mod_df", mod_df)

# Initialise other session_state variables
st.session_state.setdefault("ranked_df", None)
st.session_state.setdefault("starred_id", None)
st.session_state.setdefault("active_mode", None)  # "description" | "star"

DISPLAY_COLUMNS = {"id": "ID", "job_title": "Job Title", "location": "Location", "connection": "Connections"}

# Main layout:
st.title("Talent Recommender")
st.markdown(
    "Describe the role you're hiring for to surface the best-fit candidates, "
    "then **star** a promising result to find more people like them."
)

tab_search, tab_browse = st.tabs(["Find Candidates", "Browse All"])

# Entry point: describe the role, get ranked candidates, then star one to refine further
with tab_search:
    st.subheader("1. Describe your ideal candidate")

    description = st.text_area(
        "Role description",
        placeholder="e.g. a graduate with an interest in HR",
        height=130,
        key="desc_input",
    )

    top_n = st.slider("Show top N results", 5, 50, 20, key="top_n")

    if st.button("Find matching candidates", key="btn_desc"):
        if not description.strip():
            st.warning("Please enter a description first.")
        else:
            with st.spinner("Analysing description and ranking candidates…"):
                ranked = rank_by_description(st.session_state.mod_df, description.strip(), top_n=top_n)
            st.session_state.ranked_df = ranked
            st.session_state.starred_id = None
            st.session_state.active_mode = "description"

    if st.session_state.ranked_df is not None:
        st.divider()
        ranked = st.session_state.ranked_df

        if st.session_state.active_mode == "star":
            starred_row = st.session_state.df[st.session_state.df["id"] == st.session_state.starred_id].iloc[0]
            st.subheader(f"Results — ranked by similarity to #{starred_row['id']} ({starred_row['job_title']})")
        else:
            st.subheader("2. Results")

        if ranked.empty:
            st.info("No candidates found. Try a different query.")
        else:
            display_ranked_df = ranked[["id", "job_title", "connection", "location", "similarity_score"]]
            st.dataframe(display_ranked_df, use_container_width=True, hide_index=True)

            with st.expander("Score distribution", expanded=False):
                chart_data = ranked[["similarity_score"]].copy()
                chart_data.index = [f"#{r['id']}" for _, r in ranked.iterrows()]
                st.bar_chart(chart_data)

            st.divider()
            st.subheader("3. Star a candidate to find more like them")

            star_options = {
                f"#{row['id']} — {row['job_title'][:60]}": row["id"] for _, row in ranked.iterrows()
            }
            selected_label = st.selectbox(
                "Select a candidate from the results above",
                options=["— choose —"] + list(star_options.keys()),
                key="star_select",
            )

            if st.button("⭐ Rank by this candidate", key="btn_star"):
                if selected_label == "— choose —":
                    st.warning("Please select a candidate first.")
                else:
                    cid = star_options[selected_label]
                    with st.spinner("Ranking…"):
                        new_ranked = rank_by_starred(st.session_state.mod_df, cid, top_n=top_n)
                    st.session_state.ranked_df = new_ranked
                    st.session_state.starred_id = cid
                    st.session_state.active_mode = "star"
                    st.session_state.pop("star_select", None)
                    st.rerun()

# Browse the 'database'
with tab_browse:
    st.subheader("All Candidates")
    st.divider()

    display_df = st.session_state.df[list(DISPLAY_COLUMNS)].rename(columns=DISPLAY_COLUMNS)
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=500)
