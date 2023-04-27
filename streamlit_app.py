import scholarpy
import streamlit as st
from streamlit_option_menu import option_menu
from apps import grant, home, google, journal, orcid, organization, publication, researcher

st.set_page_config(page_title="Scholar Web App",
                   page_icon="chart_with_upwards_trend",
                   layout="wide")

# A dictionary of apps in the format of {"App title": "App icon"}
# More icons can be found here: https://icons.getbootstrap.com

apps = {"home": {"title": "Home", "icon": "house"},
        "grant": {"title": "Grant", "icon": "coin"},
        "journal": {"title": "Journal", "icon": "journals"},
        "publication": {"title": "Publication", "icon": "journal"},
        "researcher": {"title": "Researcher", "icon": "person-circle"},
        "orcid": {"title": "ORCID", "icon": "person-square"},
        "organization": {"title": "Organization", "icon": "building"},
        "google": {"title": "Google Scholar", "icon": "google"},

        }


titles = [app["title"] for app in apps.values()]
icons = [app["icon"] for app in apps.values()]
params = st.experimental_get_query_params()

if "page" in params:
    default_index = int(titles.index(params["page"][0].lower()))
else:
    default_index = 0

with st.sidebar:
    selected = option_menu(
        "Main Menu",
        options=titles,
        icons=icons,
        menu_icon="cast",
        default_index=default_index,
    )

    # st.sidebar.title("About")
    st.sidebar.info(
        """
        **Web App URL:** 
        <https://scholar.streamlit.app>

        **Contact:**
        - [Qiusheng Wu](https://geography.utk.edu/about-us/faculty/dr-qiusheng-wu)
    """
    )
    st.image("https://i.imgur.com/2WhANKg.png")

if "dsl" not in st.session_state:
    st.session_state["dsl"] = scholarpy.Dsl()

for app in apps:
    if apps[app]["title"] == selected:
        eval(f"{app}.app()")
        break
