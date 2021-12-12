import streamlit as st
from multiapp import MultiApp
from apps import h_index, journal, orcid, researcher

st.set_page_config(layout="wide")


apps = MultiApp()

# Add all your application here

apps.add_app("Search by Journal", journal.app)
apps.add_app("Get Education Data from ORCID", orcid.app)
apps.add_app("H-index", h_index.app)
apps.add_app("Researcher", researcher.app)

# The main app
apps.run()
