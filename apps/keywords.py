import os
import scholarpy
import pandas as pd
import streamlit as st
import leafmap.foliumap as leafmap
import plotly.express as px

if "dsl" not in st.session_state:
    st.session_state["dsl"] = scholarpy.Dsl()


def app():
    st.title("Search Publications by Keywords")
    dsl = st.session_state["dsl"]

    row1_col1, row1_col2, row1_col3 = st.columns(3)

    with row1_col1:
        keywords = st.text_input("Enter a keyword to search for")

    with row1_col2:
        scope = st.selectbox(
            "Select a search scope",
            [
                "authors",
                "concepts",
                "full_data",
                "full_data_exact",
                "title_abstract_only",
                "title_only",
            ],
            index=5,
        )

    with row1_col3:
        limit = st.slider("Select the number of publications to return", 1, 1000, 100)

    if keywords:
        result = dsl.search_pubs_by_keywords(keywords, scope, limit=limit)
        df = scholarpy.json_to_df(result)
        if limit > result.count_total:
            limit = result.count_total
        markdown = f"""
        Returned Publications: {limit} (total = {result.count_total})        
        
        """
        st.markdown(markdown)
        st.dataframe(df)
