from geemap.common import ee_initialize
import requests
import folium
import scholarpy
import streamlit as st
import geemap.foliumap as geemap

if "dsl" not in st.session_state:
    st.session_state["dsl"] = scholarpy.Dsl()


def get_orcid_data(orcid, info_type=None):
    """Retrieve ORCID data based on an ORCID and information type.

    Args:
        orcid (str): The ORCID to retrieve data for, e.g., 0000-0001-5437-4073
        info_type (str): The type of information to retrieve, e.g., educations, employments, works

    Returns:
        dict: The ORCID data as a dictionary.
    """
    headers = {
        "Accept": "application/vnd.orcid+json",
    }

    if info_type is not None:
        url = f"https://pub.orcid.org/v3.0/{orcid}/{info_type}"
    else:
        url = f"https://pub.orcid.org/v3.0/{orcid}"

    response = requests.get(url, headers=headers)
    return response.json()


def get_education_data(orcid):

    result = get_orcid_data(orcid, "educations")
    affiliations = result["affiliation-group"]
    info_dict = {}

    try:

        for affiliation in affiliations:
            summary = affiliation["summaries"][0]["education-summary"]
            name = summary["source"]["source-name"]["value"]
            role = summary["role-title"]

            organization = summary["organization"]["name"]
            start_year = summary["start-date"]["year"]["value"]
            end_year = summary["end-date"]["year"]["value"]
            # start_date = (
            #     summary["start-date"]["year"]["value"]
            #     + "-"
            #     + summary["start-date"]["month"]["value"]
            #     + "-"
            #     + summary["start-date"]["day"]["value"]
            # )
            # end_date = (
            #     summary["end-date"]["year"]["value"]
            #     + "-"
            #     + summary["end-date"]["month"]["value"]
            #     + "-"
            #     + summary["end-date"]["day"]["value"]
            # )
            city = summary["organization"]["address"]["city"]
            region = summary["organization"]["address"]["region"]
            country = summary["organization"]["address"]["country"]
            address_list = [city, region, country]
            address = ", ".join([i for i in address_list if i])

            # address = city + ", " + region + ", " + country
            coords = geemap.geocode(address)[0]
            lat = coords.lat
            lng = coords.lng

            info_dict[role] = {
                "name": name,
                "organization": organization,
                "start_year": start_year,
                "end_year": end_year,
                "city": city,
                "region": region,
                "country": country,
                "address": address,
                "lat": lat,
                "lng": lng,
            }
    except:
        pass

    return info_dict


def app():

    dsl = st.session_state["dsl"]
    st.title("Retrieve ORCID Data")
    m = geemap.Map(center=(20, 0), zoom=2, ee_initialize=False)

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        name = st.text_input("Enter a researcher name", "")

    if name:
        orcids = dsl.search_orcid_by_name(name, return_list=True)
        with row1_col2:
            if orcids is not None:
                selected = st.selectbox("Select an ORCID", orcids)
            else:
                selected = None
                st.write("No ORCID found.")

        #     orcids = ["0000-0001-5437-4073", "0000-0001-6157-5519"]
        #     if st.session_state.get("orcids", []) is not None:
        #         orcids = orcids + st.session_state.get("orcids", [])
        #     selected_orcid = st.selectbox("Select an ORCID:", orcids)

        # with row1_col2:
        #     orcid = st.text_input("Enter an ORCID:", selected_orcid)

        row2_col1, row2_col2 = st.columns([1, 1])

        if selected is not None:
            orcid = selected.split("|")[1].strip()
            education_data = get_education_data(orcid)
            roles = list(education_data.keys())

            for role in roles:
                popup = f"<b>Name: </b>{education_data[role]['name']}<br><b>Organization: </b>{education_data[role]['organization']}<br><b>Degree: </b>{role}"
                marker = folium.Marker(
                    [education_data[role]["lat"], education_data[role]["lng"]],
                    popup=popup,
                )
                marker.add_to(m)

            with row2_col1:
                markdown = f"""ORCID URL: <https://orcid.org/{orcid}>"""
                st.markdown(markdown)
                if len(education_data) > 0:
                    st.write("Education:")
                    st.write(education_data)
                else:
                    st.write("No education data found.")
            with row2_col2:
                m.to_streamlit()
