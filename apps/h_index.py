import dimcli
import pandas as pd
import sys
import os
import streamlit as st
import scholarpy

if "dsl" not in st.session_state:
    st.session_state["dsl"] = scholarpy.Dsl()


@st.cache
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


def dim_login(key=None, endpoint=None):

    if key is None:
        KEY = os.environ.get("DIM_TOKEN")

    if endpoint is None:
        ENDPOINT = "https://app.dimensions.ai"

    try:
        dimcli.login(key=KEY, endpoint=ENDPOINT)
        dsl = dimcli.Dsl()
        return dsl
    except:
        raise Exception("Failed to login to Dimensions")


@st.cache
def get_pubs_df(dsl, researcher_id):

    q = """search publications where researchers.id = "{}" return publications[id+title+doi+times_cited] sort by times_cited limit 1000"""

    pubs = dsl.query(q.format(researcher_id))
    return pubs.as_dataframe()


@st.cache
def get_citations(df):
    return list(df.fillna(0)["times_cited"])


def app():

    dsl = st.session_state["dsl"]

    researchER_id = st.text_input("Enter researcher ID:", "ur.013632443777.66")
    df = get_pubs_df(dsl, researchER_id)
    st.dataframe(df)
    citations = get_citations(df)
    h_index = the_H_function(citations)
    st.write(f"H-index: {h_index}")
