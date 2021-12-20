import scholarpy
import streamlit as st
from multiapp import MultiApp
from apps import grant, home, journal, orcid, publication, researcher

st.set_page_config(layout="wide")

if "dsl" not in st.session_state:
    st.session_state["dsl"] = scholarpy.Dsl()

apps = MultiApp()

# Add all your application here

apps.add_app("Home", home.app)
apps.add_app("Grant", grant.app)
apps.add_app("Journal", journal.app)
apps.add_app("Publication", publication.app)
apps.add_app("Researcher", researcher.app)
apps.add_app("ORCID", orcid.app)

# The main app
apps.run()
