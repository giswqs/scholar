import os
import scholarpy
import pandas as pd
import streamlit as st
import leafmap.foliumap as leafmap
import plotly.express as px

if "dsl" not in st.session_state:
    st.session_state["dsl"] = scholarpy.Dsl()


def app():
    st.title("Search Grants by Keyword")
    dsl = st.session_state["dsl"]

    (
        row1_col1,
        row1_col2,
        row1_col3,
        row1_col4,
        row1_col5,
    ) = st.columns([1, 0.5, 1, 1, 1])

    (
        row2_col1,
        row2_col2,
        row2_col3,
        row2_col4,
        row2_col5,
    ) = st.columns([1, 0.5, 1, 1, 1])

    with row1_col1:
        keywords = st.text_input("Enter a keyword to search for")

    with row1_col2:
        exact_match = st.checkbox("Exact match", True)

    with row1_col3:
        scope = st.selectbox(
            "Select a search scope",
            [
                "concepts",
                "full_data",
                "investigators",
                "title_abstract_only",
                "title_only",
            ],
            index=4,
        )
    with row1_col4:
        years = st.slider("Select the start and end year:", 1950, 2030, (2010, 2025))

    with row1_col5:
        limit = st.slider("Select the number of grants to return", 1, 1000, 100)

    if keywords:
        result = dsl.search_grants_by_keyword(
            keywords,
            exact_match,
            scope,
            start_year=years[0],
            end_year=years[1],
            limit=limit,
        )
        df = scholarpy.json_to_df(result)
        if limit > result.count_total:
            limit = result.count_total
        markdown = f"""
        Returned grants: {limit} (total = {result.count_total})        
        
        """
        with row2_col1:
            st.markdown(markdown)

        with row2_col2:
            filter = st.checkbox("Apply a filter")

        if filter:
            countries = []
            for row in df.itertuples():
                countries.append(eval(row.funder_countries)[0]["name"])
            df["funder_country"] = countries
            with row2_col3:
                filter_by = st.selectbox(
                    "Select a filter",
                    [
                        "funder_country",
                        "funding_org_name",
                        "funding_org_acronym",
                        "research_org_name",
                    ],
                )

                df["funding_org_acronym"] = df["funding_org_acronym"].astype(str)
                df["research_org_name"] = df["research_org_name"].astype(str)
                options = df[filter_by].unique()
                options.sort()

            with row2_col4:
                selected = st.selectbox("Select a filter value", options)
                df = df[df[filter_by] == selected]

            with row2_col5:
                st.write("")

        if df is not None:
            st.dataframe(df)
            leafmap.st_download_button("Download data", df, csv_sep="\t")
