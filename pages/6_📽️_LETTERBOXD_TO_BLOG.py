"""
AUTHOR: @highnessatharva<highnessatharva@gmail.com>

DATE: 2023-03-13

DESCRIPTION: Automatically generates a markdown file containing all your reviews and ratings for the movies you have watched in the latest month, with an upper limit of 50. Takes the RSS feed URL of a user as input.

API KEY: None 
"""

from datetime import datetime

import feedparser
import streamlit as st
from bs4 import BeautifulSoup
from mdutils.mdutils import MdUtils

st.set_page_config(
    page_title="Letterboxd To Markdown",
    page_icon="📽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# PAGE TITLE
st.title(":red[Letterboxd] To Blog :star:")

# INTRO
st.markdown(
    """   
    
    Letterboxd To Blog is a service designed to simplify the process of generating blog posts based on the movies you have watched on Letterboxd. With Letterboxd To Blog, you can easily create a markdown file containing all your reviews and ratings for the movies you have watched in the latest month, with an upper limit of 50. This tool is perfect for anyone who wants to automate the process of creating blog posts based on their movie reviews and ratings, and it's especially useful for avid movie fans who want to share their thoughts on the latest films they have watched. With Letterboxd To Blog, you can quickly and easily create high-quality blog posts without spending hours writing and formatting each individual post.  
    
    You can also generate blogs for your friends by simply entering their Letterboxd RSS feed URL. No need about authentication.
    
    Note to Self - Run this script near every month end to generate a new blog post. If you want to generate a blog post for a specific month, then you can change the `datetime.now().month` to the month you want to generate the blog post for.
    
    **Steps to get your Diary RSS**: 
    
    **EASY WAY**:   
    `https://letterboxd.com/{YOUR_LETTERBOXD_USERNAME_HERE}/rss/`
    
    **HARD WAY**:
    - Open your web browser and navigate to the [Letterboxd](https://letterboxd.com/) website

    - Log in to your account by clicking on the "Sign In" button in the top right corner of the page and entering your email address and password.

    - Once you are logged in, hover your mouse over the "Profile" button in the top right corner of the page. This should open a dropdown menu.

    - In the dropdown menu, click on the "Diary" link. This will take you to your diary page.

    - On your diary page, look for the small grey RSS feed icon in the top right corner of the page, just above the list of movies.

    - Right-click on the RSS feed icon and select "Copy link address" from the context menu. This will copy the URL of your Letterboxd diary RSS feed to your clipboard. Paste it below.
    """
)

st.write("---")

rss_to_fetch = st.text_input("Enter your Letterboxd RSS feed URL")
# tmdb_api_key=st.text_input("Enter your TMDB API key")
submit = st.button("Submit")

if rss_to_fetch and submit:

    # validate rss feed
    feed = feedparser.parse(rss_to_fetch)
    if feed.bozo == 1:
        st.error("Invalid RSS feed URL")
        st.stop()
    else:
        st.empty()

        with st.spinner(f"Getting data for the feed ↪️ {feed.feed.title}"):

            # get the feed
            d = feedparser.parse(rss_to_fetch)

            # filter only entries with current month

            # NOTE: change the datetime.now().month to the month you want to generate the blog post for
            d.entries = [
                entry
                for entry in d.entries
                if int(entry.letterboxd_watcheddate[5:7].lstrip("0"))
                == datetime.now().month
            ]

            st.write(f"Found {len(d.entries)} entries for the current month.")
        with st.spinner(
            f"Processing {len(d.entries)} entries. Writing to markdown file."
        ):

            movies = []

            titles = [entry.title for entry in d.entries]
            links = [entry.link for entry in d.entries]
            descriptions = [entry.description for entry in d.entries]

            imgs = []
            # get the <letterboxd:watchedDate> tag from the feed
            watch_dates = [entry.letterboxd_watcheddate for entry in d.entries]

            for description in descriptions:
                original_description = description
                soup = BeautifulSoup(description, "html.parser")
                first_p = soup.find("p")
                img_src = first_p.find("img")["src"]
                imgs.append(img_src)

                # new_description = re.sub('<p>[^<]*</p>', '', original_description, count=1)
                new_description = BeautifulSoup(
                    original_description, "html.parser"
                ).get_text()

                # st.write(new_description)

                # # replace the current description with the new one
                descriptions[descriptions.index(original_description)] = new_description

            # write it to a markdown file

            mdFile = MdUtils(
                file_name="Letterboxd to Blog", title="Movie Reviews: March 2023"
            )

            # zip into a tuple and add to movies
            for movie in zip(titles, links, imgs, watch_dates, descriptions):
                title = movie[0]
                link = movie[1]
                img = movie[2]
                watched_on = movie[3]
                # convert this 2023-03-04 format to 4th March 2023
                watched_on = datetime.strptime(watched_on, "%Y-%m-%d").strftime(
                    "%d %B %Y"
                )
                description = movie[4]

                mdFile.new_header(level=1, title=title)
                mdFile.new_line(mdFile.new_inline_image(text=title, path=img))
                mdFile.new_paragraph(f"**Watched on**: {watched_on}")
                mdFile.new_paragraph("**Review**")
                mdFile.new_paragraph(description)

                mdFile.new_paragraph(
                    mdFile.new_inline_link(link=link, text="Read on Letterboxd")
                )

            mdFile.create_md_file()

        st.success("Your markdown file is ready.")
        with open("Letterboxd to Blog.md", "rb") as file:
            btn = st.download_button(
                label="Download Movie Reviews",
                data=file,
                file_name="Movie Reviews.md",
                mime="text/markdown",
            )
