import streamlit as st


def app():
    st.title("Home")
    st.text(
        "Welcome to the Scholar Web App. Click on the left sidebar menu to explore."
    )
    markdown = """
    Disclaimer: The data records are pulled from the [Dimensions.ai database](https://app.dimensions.ai), which might be be the most complete bibliometric database.
    We plan to incorporate [Scopus](https://www.scopus.com) and [Google Scholar](https://scholar.google.com) in the near future. Don't be surprised if you see that 
    your publication records are not the same as your Google Scholar profile. This is a very preliminary version. A lot more features will be added in the future.
    We would welcome any feedback. Please send feedback to Qiusheng Wu (qwu18@utk.edu).
    """
    st.info(markdown)
    st.image("https://i.imgur.com/ZNUJ9fF.gif")
