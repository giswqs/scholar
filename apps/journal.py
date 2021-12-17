import os
import json
import dimcli
import pandas as pd
import plotly.express as px
import streamlit as st
import scholarpy
import leafmap.foliumap as leafmap

if "dsl" not in st.session_state:
    st.session_state["dsl"] = scholarpy.Dsl()

# create output data folder
FOLDER_NAME = "data"
if not (os.path.exists(FOLDER_NAME)):
    os.mkdir(FOLDER_NAME)


def save(df, filename_dot_csv):
    df.to_csv(FOLDER_NAME + "/" + filename_dot_csv, index=False)


def read(filename_dot_csv):
    df = pd.read_csv(FOLDER_NAME + "/" + filename_dot_csv)
    return df


@st.cache
def get_token():

    return os.environ.get("DIM_TOKEN")


@st.cache
def get_journals():

    with open("data/journals.json") as f:
        journals = json.load(f)

    return journals


@st.cache
def read_excel(sheet_name):

    df = pd.read_excel(
        "data/journals.xlsx", sheet_name=sheet_name, index_col=False, engine="openpyxl"
    )
    df.set_index("Rank", inplace=True)
    return df


def app():

    st.title("Search Journal")
    dsl = st.session_state["dsl"]
    search_type = st.radio(
        "Select a search type",
        ["Search by journal title", "List Google Scholar journal categories"],
    )

    if search_type == "Search by journal title":
        row1_col1, row1_col2, row1_col3, _ = st.columns([1, 1, 2, 1])
        with row1_col1:
            name = st.text_input("Enter a journal title")

        with row1_col2:
            exact_match = st.checkbox("Exact match")

        with row1_col3:
            options = ["book_series", "proceeding", "journal", "preprint_platform"]
            types = st.multiselect(
                "Select journal types", options, ["journal", "book_series"]
            )

        if name:
            titles = dsl.search_journal_by_title(
                name, exact_match=exact_match
            ).as_dataframe()
            titles = titles[titles["type"].isin(types)]
            # titles = titles.astype({"start_year": int})
            if not titles.empty:
                st.dataframe(titles)
                titles["uid"] = (
                    titles["id"] + " | " + titles["type"] + " | " + titles["title"]
                )

                row2_col1, row2_col2 = st.columns([3, 1])

                with row2_col1:
                    title = st.selectbox(
                        "Select a journal title", titles["uid"].values.tolist()
                    )
                with row2_col2:
                    years = st.slider(
                        "Select the start and end year:", 1950, 2021, (1980, 2021)
                    )

                if title:
                    journal_id = title.split(" | ")[0]
                    pubs = dsl.get_pubs_by_journal_id(journal_id, years[0], years[1])
                    pubs_df = pubs.as_dataframe()
                    if pubs_df is not None and (not pubs_df.empty):
                        st.write(
                            f"Total number of pulications: {pubs.count_total:,}. Display {min(pubs.count_total, 1000)} publications below."
                        )
                        try:
                            st.dataframe(pubs_df)
                        except Exception as e:
                            st.dataframe(scholarpy.json_to_df(pubs))
                            # st.error("An error occurred: " + str(e))
                        leafmap.st_download_button(
                            "Download data", pubs_df, csv_sep="\t"
                        )

    elif search_type == "List Google Scholar journal categories":

        st.markdown(
            """
        The journal categories are adopted from [Google Scholar](https://scholar.google.com/citations?view_op=top_venues&hl=en&inst=9897619243961157265).
        See the list of journals [here](https://docs.google.com/spreadsheets/d/1uCEi3TsJCWl9QEZimvjlM8wjt7hNq3QvMqHGeT44HXQ/edit?usp=sharing).
        """
        )

        st.session_state["orcids"] = None
        # dsl = st.session_state["dsl"]
        # token = get_token()
        # dimcli.login(key=token, endpoint="https://app.dimensions.ai")
        # dsl = dimcli.Dsl()

        categories = get_journals()

        row1_col1, row1_col2, _, row1_col3 = st.columns([1, 1, 0.05, 1])

        with row1_col1:
            category = st.selectbox("Select a category:", categories.keys())

        if category:
            with row1_col2:
                journal = st.selectbox("Select a journal:", categories[category].keys())

        with row1_col3:
            years = st.slider(
                "Select the start and end year:", 1950, 2021, (1980, 2021)
            )

        if journal:
            pubs = read_excel(sheet_name=category)
            with st.expander("Show journal metrics"):
                st.dataframe(pubs)

        journal_id = categories[category][journal]
        if journal_id is not None and str(journal_id).startswith("jour"):
            q_template = """search publications where
                journal.id="{}" and
                year>={} and 
                year<={}
                return publications[id+title+doi+year+authors+type+pages+journal+issue+volume+altmetric+times_cited]
                limit 1000"""
            q = q_template.format(journal_id, years[0], years[1])
        else:
            q_template = """search publications where
                journal.title="{}" and
                year>={} and 
                year<={}
                return publications[id+title+doi+year+authors+type+pages+journal+issue+volume+altmetric+times_cited]
                limit 1000"""
            q = q_template.format(journal, years[0], years[1])

        pubs = dsl.query(q)
        if pubs.count_total > 0:
            st.header("Publications")
            st.write(
                f"Total number of pulications: {pubs.count_total:,}. Display 1,000 publications below."
            )
            df_pubs = pubs.as_dataframe()
            save(df_pubs, "publications.csv")
            df_pubs = read("publications.csv")
            st.dataframe(df_pubs)

            st.header("Authors")
            authors = pubs.as_dataframe_authors()
            st.write(
                f"Total number of authors of the 1,000 pubs shown above: {authors.shape[0]:,}"
            )
            save(authors, "authors.csv")
            df_authors = read("authors.csv")
            st.dataframe(df_authors)

            df_authors_orcid = df_authors[~df_authors["orcid"].isna()]
            # st.dataframe(df_authors_orcid)
            orcids = list(set(df_authors_orcid["orcid"].values.tolist()))
            orcids = [i[2:21] for i in orcids]
            orcids.sort()
            # st.write(orcids)
            st.session_state["orcids"] = orcids

            st.header("Affiliations")
            affiliations = pubs.as_dataframe_authors_affiliations()
            st.write(
                f"Total number of affiliations of the 1,000 pubs shown above: {affiliations.shape[0]:,}"
            )
            save(affiliations, "affiliations.csv")
            df_affiliations = read("affiliations.csv")
            st.dataframe(df_affiliations)

            researchers = authors.query("researcher_id!=''")
            #
            df_researchers = pd.DataFrame(
                {
                    "measure": [
                        "Authors in total (non unique)",
                        "Authors with a researcher ID",
                        "Authors with a researcher ID (unique)",
                    ],
                    "count": [
                        len(authors),
                        len(researchers),
                        researchers["researcher_id"].nunique(),
                    ],
                }
            )
            fig_researchers = px.bar(
                df_researchers,
                x="measure",
                y="count",
                title=f"Author Research ID stats for {journal} ({years[0]}-{years[1]})",
            )

            orcids = authors.query("orcid!=''")
            #
            df_orcids = pd.DataFrame(
                {
                    "measure": [
                        "Authors in total (non unique)",
                        "Authors with a ORCID",
                        "Authors with a ORCID (unique)",
                    ],
                    "count": [
                        len(authors),
                        len(orcids),
                        orcids["orcid"].nunique(),
                    ],
                }
            )
            fig_orcids = px.bar(
                df_orcids,
                x="measure",
                y="count",
                title=f"Author ORCID stats for {journal} ({years[0]}-{years[1]})",
            )

            st.header("Stats")

            row2_col1, row1_col2 = st.columns(2)
            with row2_col1:
                st.plotly_chart(fig_researchers)
            with row1_col2:
                st.plotly_chart(fig_orcids)

        else:
            st.warning("No publications found")
