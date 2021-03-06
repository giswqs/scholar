import os
import scholarpy
import pandas as pd
import streamlit as st
import leafmap.foliumap as leafmap
import plotly.express as px

if "dsl" not in st.session_state:
    st.session_state["dsl"] = scholarpy.Dsl()


@st.cache(allow_output_mutation=True)
def get_geonames():
    return scholarpy.get_geonames()


def json_to_df(json_data, transpose=False):
    df = json_data.as_dataframe()
    if not df.empty:
        if transpose:
            df = df.transpose()

        out_csv = leafmap.temp_file_path(".csv")
        df.to_csv(out_csv, index=transpose)
        df = pd.read_csv(out_csv)
        os.remove(out_csv)
        return df
    else:
        return None


def annual_pubs(pubs, col="year"):
    if pubs is not None:
        df = pubs[col].value_counts().sort_index()
        df2 = pd.DataFrame({"year": df.index, "publications": df.values})
        return df2
    else:
        return None


def annual_collaborators(pubs, col="year"):
    if pubs is not None:
        df = pubs.groupby([col]).sum()
        df2 = pd.DataFrame(
            {"year": df.index, "collaborators": df["authors_count"].values}
        )
        fig = px.bar(
            df2,
            x="year",
            y="collaborators",
        )
        return fig
    else:
        return None


def annual_citations(pubs, col="year"):
    if pubs is not None:
        df = pubs.groupby([col]).sum()
        df2 = pd.DataFrame(
            {"year": df.index, "citations": df["times_cited"].values})
        fig = px.bar(
            df2,
            x="year",
            y="citations",
        )
        return fig
    else:
        return None


def the_H_function(sorted_citations_list, n=1):
    """from a list of integers [n1, n2 ..] representing publications citations,
    return the max list-position which is >= integer

    eg
    >>> the_H_function([10, 8, 5, 4, 3]) => 4
    >>> the_H_function([25, 8, 5, 3, 3]) => 3
    >>> the_H_function([1000, 20]) => 2
    """
    if sorted_citations_list and sorted_citations_list[0] >= n:
        return the_H_function(sorted_citations_list[1:], n + 1)
    else:
        return n - 1


def app():

    st.title("Search Researchers")
    dsl = st.session_state["dsl"]
    row1_col1, row1_col2 = st.columns([1, 1])

    with row1_col1:
        name = st.text_input("Enter a researcher name:", "")

    if name:

        ids, names = dsl.search_researcher_by_name(name, return_list=True)
        if ids.count_total > 0:
            # options = ids.as_dataframe()["id"].values.tolist()
            with row1_col1:
                name = st.selectbox("Select a researcher id:", names)

            if name:
                id = name.split("|")[1].strip()
                id_info = dsl.search_researcher_by_id(id, return_df=False)

                info_df = json_to_df(id_info, transpose=True)
                info_df.rename(
                    columns={info_df.columns[0]: "Type",
                             info_df.columns[1]: "Value"},
                    inplace=True,
                )
                with row1_col1:
                    st.header("Researcher Information")
                    if not info_df.empty:
                        st.dataframe(info_df)
                        leafmap.st_download_button(
                            "Download data", info_df, csv_sep="\t"
                        )
                    else:
                        st.text("No information found")

                pubs = dsl.search_pubs_by_researcher_id(id)
                df = json_to_df(pubs)
                # annual_df = annual_pubs(df)
                if df is not None:
                    df1, df2 = dsl.researcher_annual_stats(
                        pubs, geonames_df=get_geonames()
                    )
                    df3 = scholarpy.collaborator_locations(df2)

                    with row1_col2:
                        st.header("Researcher statistics")
                        columns = ["pubs", "collaborators",
                                   "institutions", "cities"]
                        selected_columns = st.multiselect(
                            "Select attributes to display:", columns, columns
                        )
                        if selected_columns:
                            fig = scholarpy.annual_stats_barplot(
                                df1, selected_columns)
                            st.plotly_chart(fig)
                        leafmap.st_download_button(
                            "Download data",
                            df1,
                            file_name="data.csv",
                            csv_sep="\t",
                        )

                        st.header("Map of collaborator institutions")
                        markdown = f"""
                        - Total number of collaborator institutions: **{len(df3)}**
                        """
                        st.markdown(markdown)
                        m = leafmap.Map(
                            center=[0, 0],
                            zoom_start=1,
                            latlon_control=False,
                            draw_control=False,
                            measure_control=False,
                            locate_control=True,
                        )
                        m.add_points_from_xy(df3)
                        m.to_streamlit(height=420)
                        leafmap.st_download_button(
                            "Download data",
                            df3,
                            file_name="data.csv",
                            csv_sep="\t",
                        )

                        st.header("Publication counts with collaborators")
                        collaborators = dsl.search_researcher_collaborators(
                            id, pubs)
                        markdown = f"""
                        - Total number of collaborators: **{len(collaborators)}**
                        """
                        st.markdown(markdown)
                        st.dataframe(collaborators)
                        leafmap.st_download_button(
                            "Download data",
                            collaborators,
                            file_name="data.csv",
                            csv_sep="\t",
                        )
                else:
                    st.text("No publications found")

                with row1_col1:
                    st.header("Publications")
                    if df is not None:
                        citations = df["times_cited"].values.tolist()
                        citations.sort(reverse=True)
                        h_index = the_H_function(citations)
                        markdown = f"""
                        - Total number of publications: **{len(df)}**
                        - Total number of citations: **{df["times_cited"].sum()}**
                        - i10-index: **{len(df[df["times_cited"]>=10])}**
                        - h-index: **{h_index}**
                        """
                        st.markdown(markdown)
                        st.dataframe(df)
                        leafmap.st_download_button(
                            "Download data", df, file_name="data.csv", csv_sep="\t"
                        )

                        if "journal.title" in df.columns:
                            st.header("Publication counts by journal")
                            journals = df["journal.title"].value_counts()
                            summary = pd.DataFrame(
                                {"Journal": journals.index, "Count": journals}
                            ).reset_index(drop=True)
                            markdown = f"""
                            - Total number of journals: **{len(summary)}**
                            """
                            st.markdown(markdown)
                            st.dataframe(summary)
                            leafmap.st_download_button(
                                "Download data",
                                summary,
                                file_name="data.csv",
                                csv_sep="\t",
                            )
                        else:
                            st.text("No journal publications")

                    else:
                        st.text("No publications found")

                    grants = dsl.search_grants_by_researcher(id)
                    df = grants.as_dataframe()
                    if not df.empty:
                        st.header("Grants")
                        st.dataframe(df)
                        leafmap.st_download_button(
                            "Download data", df, file_name="data.csv", csv_sep="\t"
                        )
        else:
            st.text("No results found.")
