import os
import scholarpy
import pandas as pd
import streamlit as st
import leafmap.foliumap as leafmap
import plotly.express as px

if "dsl" not in st.session_state:
    st.session_state["dsl"] = scholarpy.Dsl()


def app():

    st.title("Search Organizations")
    dsl = st.session_state["dsl"]
    row1_col1, row1_col2 = st.columns([1, 1])

    with row1_col1:
        name = st.text_input("Enter an organization name:", "")

    if name:
        orgs = dsl.search_org_by_name(
            name, exact_match=False, return_list=True)

        if orgs is not None:
            with row1_col1:
                selected_org = st.selectbox("Select a organization id:", orgs)
                org_id = selected_org.split("|")[0].strip()

                id_info = dsl.search_org_by_id(org_id)

                info_df = scholarpy.json_to_df(id_info, transpose=True)
                info_df.rename(
                    columns={info_df.columns[0]: "Type",
                             info_df.columns[1]: "Value"},
                    inplace=True,
                )
                with row1_col1:
                    st.header("Organization Information")
                    if not info_df.empty:
                        st.dataframe(info_df)
                        leafmap.st_download_button(
                            "Download data", info_df, csv_sep="\t"
                        )
                    else:
                        st.text("No information found")

                with row1_col2:
                    st.header("Publications by year")

                    years = st.slider(
                        "Select the start and end year:", 1950, 2030, (1980, 2021))

                    pubs, fig = dsl.org_pubs_annual_stats(
                        org_id, start_year=years[0], end_year=years[1], return_plot=True)

                    st.text(
                        f'Total number of publications: ${pubs["count"].sum():,}')

                    if fig is not None:
                        st.plotly_chart(fig)

                        leafmap.st_download_button(
                            "Download data",
                            pubs,
                            file_name="data.csv",
                            csv_sep="\t",
                        )
                    else:
                        st.text("No publications found")

                    st.header("Top funders")

                    funder_count = st.slider(
                        "Select the number of funders:", 1, 100, 20)

                    funders, fig = dsl.org_grant_funders(
                        org_id, limit=funder_count, return_plot=True)
                    st.text(
                        f'Total funding amount: ${funders["funding"].sum():,}')
                    if fig is not None:
                        st.plotly_chart(fig)
                        leafmap.st_download_button(
                            "Download data",
                            funders,
                            file_name="data.csv",
                            csv_sep="\t",
                        )
                    else:
                        st.text("No funders found")

        else:
            st.text("No organizations found")
