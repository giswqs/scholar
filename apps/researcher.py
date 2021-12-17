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
        df2 = pd.DataFrame({"year": df.index, "citations": df["times_cited"].values})
        fig = px.bar(
            df2,
            x="year",
            y="citations",
        )
        return fig
    else:
        return None


def app():

    st.title("Search Researcher by Name")
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
                    columns={info_df.columns[0]: "Type", info_df.columns[1]: "Value"},
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

                pubs = dsl.get_pubs_by_researcher_id(id, extra=True)
                df = json_to_df(pubs)
                # annual_df = annual_pubs(df)
                if df is not None:
                    df1, df2 = dsl.researcher_annual_stats(
                        pubs, geonames_df=get_geonames()
                    )
                    df3 = scholarpy.collaborator_locations(df2)

                    with row1_col2:
                        st.header("Researcher statistics")
                        columns = ["pubs", "collaborators", "institutions", "cities"]
                        selected_columns = st.multiselect(
                            "Select attributes to display:", columns, columns
                        )
                        if selected_columns:
                            fig = scholarpy.annual_stats_barplot(df1, selected_columns)
                            st.plotly_chart(fig)

                        st.header("Map of collaborator institutions")
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

                else:
                    st.text("No publications found")

                with row1_col1:
                    st.header("Publications")
                    if df is not None:
                        st.dataframe(df)
                        leafmap.st_download_button(
                            "Download data", df, file_name="data.csv", csv_sep="\t"
                        )
                    else:
                        st.text("No publications found")
        else:
            st.text("No results found.")
