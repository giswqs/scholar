import os
import scholarpy
import pandas as pd
import streamlit as st
import leafmap.foliumap as leafmap
import plotly.express as px

if "dsl" not in st.session_state:
    st.session_state["dsl"] = scholarpy.Dsl()


def app():
    st.title("Search Publications")
    dsl = st.session_state["dsl"]

    (
        row1_col1,
        row1_col2,
        row1_col3,
        row1_col4,
        row1_col5,
    ) = st.columns([1, 0.7, 1, 1, 1])

    row2_col1, row2_col2, row2_col3, row2_col4, row2_col5 = st.columns(
        [1, 0.7, 1, 1, 1]
    )

    with row1_col1:
        keywords = st.text_input("Enter a keyword to search for")

    with row1_col2:
        exact_match = st.checkbox("Exact match", True)

    with row1_col3:
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

    with row1_col4:
        years = st.slider("Select the start and end year:", 1950, 2030, (1980, 2022))

    with row1_col5:
        limit = st.slider("Select the number of publications to return", 1, 1000, 100)

    if keywords:
        result = dsl.search_pubs_by_keyword(
            keywords,
            exact_match,
            scope,
            start_year=years[0],
            end_year=years[1],
            limit=limit,
        )
        df = scholarpy.json_to_df(result)
        journal_counts = df.copy()["journal.title"].value_counts()
        if limit > result.count_total:
            limit = result.count_total
        markdown = f"""
        Returned Publications: {limit} (total = {result.count_total})        
        
        """

        with row2_col1:
            st.markdown(markdown)

        with row2_col2:
            filter = st.checkbox("Filter by journal")

        if filter:
            df["journal.title"] = df["journal.title"].astype(str)
            journals = df["journal.title"].unique()
            journals.sort()
            with row2_col3:
                journal = st.selectbox("Select a journal", journals)
            df = df[df["journal.title"] == journal]

        with row2_col4:
            st.write("")

        with row2_col5:
            st.write("")

        if df is not None:
            st.dataframe(df)
            leafmap.st_download_button("Download data", df, csv_sep="\t")

            summary = pd.DataFrame(
                {"Journal": journal_counts.index, "Count": journal_counts}
            ).reset_index(drop=True)
            markdown = f"""
            - Total number of journals: **{len(summary)}**
            """
            st.markdown(markdown)
            st.dataframe(summary)
            leafmap.st_download_button("Download data", summary, csv_sep="\t")
