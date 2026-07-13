# This is the master 'src' script for the Streamlit front end that will be run by the user.

# CCDS Imports:
from pathlib import Path
from config import PROCESSED_DATA_DIR, RAW_DATA_DIR

# Base Imports:
import streamlit as st
import pandas as pd
import numpy as np

# Custom Imports:
from recommender import load_data, rank_by_starred,rank_by_description

# Import the base 'database' (csv) as a df:
from config import RAW_DATA_DIR
BASE_DATA_PATH = RAW_DATA_DIR / "potential-talents - Aspiring human resources - seeking human resources.csv"
df, mod_df = load_data(BASE_DATA_PATH)

# Define base layout:
st.set_page_config(
    page_title="Talent Recommender",
    layout="wide", # Makes the app much wider
    initial_sidebar_state="expanded"

)

# Add them to the session memory:
st.session_state.df = df
st.session_state.mod_df = mod_df

# Initialise other session_state variables
if "starred_id" not in st.session_state:
    st.session_state.starred_id = None

if "ranked_df" not in st.session_state:
    st.session_state.ranked_df = None

if "active_mode" not in st.session_state:
    st.session_state.active_mode = None   # "star" | "description"

if "active_query" not in st.session_state:
    st.session_state.active_query = ""

# Main layout:
st.title("Talent Recommender")
st.markdown(
    "Find the best-fit candidates by **starring** an existing profile or **describing** your ideal hire."
)

    # Tabs:
tab_browse, tab_search = st.tabs(
    ["Browse All","Find Candidates"]
)

# Browse the 'database'
with tab_browse:
    st.subheader("All Candidates")

    st.divider()

    display_df = st.session_state.df.copy()
    display_df_cols = display_df.columns

    st.dataframe(display_df[display_df_cols].rename(columns={"id":"ID",
                                                             "job_title":"Job Title",
                                                             "location":"Location",
                                                             "connection":"Connections"}),
                                                             use_container_width=True,
                                                             hide_index=True,
                                                             height=500
                                                             )

# Find candidates (tab_search)
with tab_search:
    col_left, col_right = st.columns([1, 1], gap="large")

    # Star an ideal candidate
    with col_left:
        st.subheader("Star a Candidate")

        df = st.session_state.df
        options = {
            f"#{row['id']} — {row['job_title'][:60]}": row["id"]
            for _, row in df.iterrows()
        }
        selected_label = st.selectbox(
            "Select candidate",
            options=["— choose —"] + list(options.keys()),
            key="star_select"
        )

        top_n_star = st.slider("Show top N results", 5, 50, 20, key="top_n_star")

        if st.button("⭐ Rank by this candidate", use_container_width=True, key="btn_star"):
            if selected_label == "— choose —":
                st.warning("Please select a candidate first.")
            else:
                cid = options[selected_label]
                with st.spinner("Ranking…"):
                    mod_df = st.session_state.mod_df # mod_df contains the 'combined' column, df doesn't
                    ranked = rank_by_starred(mod_df, cid, top_n=top_n_star) 
                st.session_state.ranked_df = ranked
                st.session_state.starred_id = cid
                st.session_state.active_mode = "star"
                st.session_state.active_query = (
                    df[df["id"] == cid].iloc[0]["job_title"]
                )

    # Describe an ideal candidate:
    with col_right:
        st.subheader("Describe your ideal candidate")

        description = st.text_area(
            "Role description",
            placeholder=("e.g. a graduate with an interest in HR"),
            height=130,
            key="desc_input"
            )
        
        top_n_desc = st.slider("Show top N results", 5, 50, 20, key="top_n_desc")

        if st.button("Find matching candidates", use_container_width=True, key="btn_desc"):
            if not description.strip():
                st.warning("Please enter a description first.")
            else:
                with st.spinner("Analysing description and ranking candidates…"):
                    ranked = rank_by_description(
                        df,
                        description.strip(),
                        top_n=top_n_desc,
                    )
                
                st.session_state.ranked_df = ranked
                st.session_state.starred_id = None
                st.session_state.active_mode = "description"
                st.session_state.active_query = description.strip()

    st.divider()
    
    # Results:
    if st.session_state.ranked_df is not None:
        ranked = st.session_state.ranked_df
        mode = st.session_state.active_mode
        query = st.session_state.active_query

        if mode == "star":
            starred_row = st.session_state.df[st.session_state.df["id"] == st.session_state.starred_id].iloc[0]
            st.markdown(f"### Results — Ranked against candidate ID {starred_row['id']}")
        
        if ranked.empty:
            st.info("No candidates found. Try a different query.")
        else:
             # Display table of results:
            display_ranked_df = ranked[["id","job_title","connection","location","similarity_score"]]
            st.dataframe(display_ranked_df)

            # Score distribution chart
            with st.expander("Score distribution", expanded=False):
                chart_data = ranked[["similarity_score"]].copy()
                chart_data.index = [f"#{r['id']}" for _, r in ranked.iterrows()]
                st.bar_chart(chart_data)
        
        
           



