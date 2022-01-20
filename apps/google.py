import os
import scholarpy
import tempfile
import pandas as pd
import streamlit as st
import leafmap.foliumap as leafmap
import plotly.express as px
from scholarly import scholarly

# if "dsl" not in st.session_state:
#     st.session_state["dsl"] = scholarpy.Dsl()


def app():

    st.title("Search Google Scholar")

    row1_col1, row1_col2 = st.columns([1, 1])

    with row1_col1:
        name = st.text_input("Enter a researcher name:", "")

    if name:
        if name not in st.session_state:
            authors = scholarpy.get_author_list(name)
            st.session_state[name] = authors
        else:
            authors = st.session_state[name]

        if len(authors) == 0:
            with row1_col1:
                st.write("No results found")
        else:
            with row1_col1:
                st.write("Found {} results:".format(len(authors)))

                author = st.selectbox("Select a researcher:", authors)

            if author:
                id = author.split("|")[1].strip()
                if id not in st.session_state:
                    record = scholarpy.get_author_record(id=id)
                    st.session_state[id] = record
                else:
                    record = st.session_state[id]
                basics = scholarpy.get_author_basics(
                    record=record, return_df=True)
                out_csv = os.path.join(tempfile.gettempdir(), "basics.csv")
                basics.to_csv(out_csv, sep="\t", index=False)
                df = pd.read_csv(out_csv, sep="\t")
                with row1_col1:
                    st.header("Basic information")
                    markdown = f"""Google Scholar Profile: <https://scholar.google.com/citations?user={id}>"""
                    st.markdown(markdown)
                    if "url_picture" in record and len(record["url_picture"]) > 0:
                        st.image(record["url_picture"])
                    st.dataframe(df)
                    leafmap.st_download_button(
                        "Download data", df, csv_sep="\t")

                pubs = scholarpy.get_author_pubs(record=record, return_df=True)
                with row1_col1:
                    st.header("Publications")
                    st.text(f"Total number of publications: {len(pubs)}")
                    st.dataframe(pubs)
                    leafmap.st_download_button(
                        "Download data", pubs, csv_sep="\t")

                pubs_stats, pubs_fig = scholarpy.author_pubs_by_year(
                    record=record, return_plot=True)
                citations_stats, citations_fig = scholarpy.author_citations_by_year(
                    record=record, return_plot=True)

                with row1_col2:
                    st.header("Plots")
                    st.plotly_chart(pubs_fig)
                    leafmap.st_download_button("Download data", pubs_stats,
                                               file_name="data.csv", csv_sep="\t")
                    st.plotly_chart(citations_fig)
                    leafmap.st_download_button(
                        "Download data", citations_stats, file_name="data.csv", csv_sep="\t")
                    if len(record["coauthors"]) > 0:
                        st.header("Co-authors")
                        st.text(
                            "Co-authors listed on Google Scholar profile only.")
                        coauthors = scholarpy.get_author_coauthors(
                            record=record, return_df=True)
                        st.dataframe(coauthors)
                        leafmap.st_download_button(
                            "Download data", coauthors, file_name="data.csv", csv_sep="\t")
