import streamlit as st
from streamlit_option_menu import option_menu
from apps import grant, home, journal, orcid, publication, researcher

st.set_page_config(layout="wide")

# A dictionary of apps in the format of {"App title": "App icon"}
# More icons can be found here: https://icons.getbootstrap.com
apps = {"Home": "house", "Grant": "coin", "Journal": "journals",
        "Publication": "journal",
        "Researcher": "person-circle", "ORCID": "person-square"}

titles = [title.lower() for title in list(apps.keys())]
params = st.experimental_get_query_params()

if "page" in params:
    default_index = int(titles.index(params["page"][0].lower()))
else:
    default_index = 0

with st.sidebar:
    selected = option_menu(
        "Main Menu",
        options=list(apps.keys()),
        icons=list(apps.values()),
        menu_icon="cast",
        default_index=default_index,
    )

    st.sidebar.title("About")
    st.sidebar.info(
        """
        The web app URL: <https://scholar.gishub.org>. If you have any questions regarding this web app, please contact [Qiusheng Wu](https://wetlands.io) (qwu18@utk.edu).
    """
    )

# Place each app module under the apps folder
if selected == "Home":
    home.app()
elif selected == "Grant":
    grant.app()
elif selected == "Journal":
    journal.app()
elif selected == "Publication":
    publication.app()
elif selected == "Researcher":
    researcher.app()
elif selected == "ORCID":
    orcid.app()
