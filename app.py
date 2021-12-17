import scholarpy
import streamlit as st
from multiapp import MultiApp
from apps import h_index, home, journal, keyword, orcid, researcher

st.set_page_config(layout="wide")

if "dsl" not in st.session_state:
    st.session_state["dsl"] = scholarpy.Dsl()

apps = MultiApp()

# Add all your application here

apps.add_app("Home", home.app)
apps.add_app("Journal", journal.app)
apps.add_app("ORCID", orcid.app)
apps.add_app("H-index", h_index.app)
apps.add_app("Researcher", researcher.app)
apps.add_app("Keyword", keyword.app)

# The main app
apps.run()
