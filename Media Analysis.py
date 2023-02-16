import streamlit as st

st.set_page_config(
    page_title="Entertainment Data Analysis",
    page_icon="🚀",
)

st.write("# Entertainment Data Analysis 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    Here, we will be analyzing data from various entertainment platforms. All you have to do is select a demo from the sidebar, upload your CSV file, and you're good to go! 🚀
    
    Currently we support the following platforms:
    - Goodreads
    - Steam
    - Letterboxd
    """
)
