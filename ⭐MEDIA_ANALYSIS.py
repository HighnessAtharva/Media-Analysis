import streamlit as st

st.set_page_config(
    page_title="Entertainment Data Analysis",
    page_icon="🚀",
)

st.write("# :violet[Entertainment] :green[Data] :green[Analysis] ⭐")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
   Are you interested in analyzing data from your favorite entertainment platforms? Look no further! Our app provides you with an easy-to-use interface for analyzing data from various entertainment platforms. 🤩

### What platforms do we support? 🔎

Currently, we support **Goodreads, Steam, and Letterboxd**. Simply select your preferred demo from the sidebar, upload your CSV file, and you're ready to go!

### Why did we build this app? 🎉

We built this app to exercise our data science skills through real-life entertainment analysis. We wanted to create a tool that makes it easy for entertainment enthusiasts to analyze data and gain insights into their favorite platforms.

### How does it work? 🚀

Our app uses Python and several data science libraries, including Pandas and Matplotlib, to perform data analysis on the CSV files uploaded by the user. The user interface is built with Streamlit, making it user-friendly and visually appealing.

### Where can you find our code? 💻

Our code is available on Github for anyone to explore and use. Feel free to check out our code, contribute, and leave us feedback!

**Github Repo: [Media Analysis Code Repo](https://github.com/HighnessAtharva/Media-Analysis)**

### Start analyzing your data today! 📈

Whether you're a data enthusiast or just curious about your entertainment habits, our app makes it easy for you to gain insights into your favorite platforms. So, what are you waiting for? Upload your CSV file and start analyzing your data today! 
    """
)
