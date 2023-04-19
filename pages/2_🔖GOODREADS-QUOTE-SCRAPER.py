"""
AUTHOR: @highnessatharva<highnessatharva@gmail.com>

DATE: 2023-02-17

DESCRIPTION: Download all quotes associated with an author from Goodreads based on the number of pages you want to scrape. The app returns a CSV file with the data. 

API KEYS: None
"""


import contextlib
import csv

import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup, NavigableString


def is_author_valid(author):
    author = author.replace(" ", "+")
    page = requests.get(
        f"https://www.goodreads.com/quotes/search?commit=Search&page=1&q={author}&utf8=%E2%9C%93"
    )
    soup = BeautifulSoup(page.text, "html.parser")
    results = soup.find(class_="mediumText").text
    # st.write(results)
    return "no results matched your search" not in results


def get_max_pages(author):
    try:
        author = author.replace(" ", "+")
        page = requests.get(
            f"https://www.goodreads.com/quotes/search?commit=Search&page=1&q={author}&utf8=%E2%9C%93"
        )
        soup = BeautifulSoup(page.text, "html.parser")
        # return number of max pages
        results = soup.find(class_="smallText").text
        a = results.find("of ")
        results = results[a + 3 :]
        # remove commas and new lines from string
        results = results.replace(",", "").replace("\n", "")
        results = int(results) // 20
        return results
    except Exception as e:
        st.error("Error getting max pages")


def scrape_quotes(author, limit, current_timestamp):
    author = author.replace(" ", "+")
    all_quotes = []
    st.write("Looking through", limit, "pages")

    with open(
        f"csvs/goodreads/quote-scraper/{author}_{current_timestamp}.csv",
        "w",
        encoding="utf-8",
        newline="",
    ) as quoteCSV:
        fieldnames = ["quote", "author", "book", "tags", "likes"]
        writer = csv.DictWriter(quoteCSV, fieldnames=fieldnames)
        writer.writeheader()

        # for each page
        for i in range(1, limit + 1):
            try:
                page = requests.get(
                    f"https://www.goodreads.com/quotes/search?commit=Search&page={str(i)}&q={author}&utf8=%E2%9C%93"
                )
                soup = BeautifulSoup(page.text, "html.parser")
                st.write("Scraping Page 📄#", i)
            except Exception as e:
                st.write("Could not connect to Goodreads. On page 📄#", i)
                continue

            with contextlib.suppress(Exception):
                quote = soup.find(class_="leftContainer")
                quote_list = quote.find_all(class_="quoteDetails")

            # get data for each quote
            for quote in quote_list:
                try:
                    outer = quote.find(class_="quoteText")
                    inner_text = [
                        element
                        for element in outer
                        if isinstance(element, NavigableString)
                    ]
                    inner_text = [x.replace("\n", "") for x in inner_text]
                    final_quote = "\n".join(inner_text[:-4]).strip()

                except Exception as e:
                    st.write("Could not get quote on page 📄#", i)
                    final_quote = None

                try:
                    author = quote.find(class_="authorOrTitle").text
                    author = author.replace(",", "")
                    author = author.strip()
                except Exception as e:
                    author = None

                try:
                    title = quote.find(class_="authorOrTitle")
                    title = title.nextSibling.nextSibling.text
                    title = title.strip()
                except Exception as e:
                    title = None

                try:
                    tags = quote.find(class_="greyText smallText left").text
                    tags = [x.strip() for x in tags.split(",")]
                    tags = tags[1:]
                    tags = None if len(tags) == 0 else ", ".join(tags)
                except Exception as e:
                    tags = None

                try:
                    likes = quote.find(class_="right").text
                    likes = likes.replace("likes", "")
                    likes = int(likes)
                except Exception as e:
                    likes = None

                writer.writerow(
                    {
                        "quote": final_quote,
                        "author": author,
                        "book": title,
                        "tags": tags,
                        "likes": likes,
                    }
                )

    st.success(f"Successfully scraped {limit} pages for {author.capitalize()}.")


# CONFIG
st.set_page_config(
    page_title="Goodreads Quote Scraper",
    page_icon="🔖",
    layout="wide",
    initial_sidebar_state="collapsed",
    # sourcery skip: use-named-expression
)

# TITLE
st.title(":violet[Goodreads] Quote Scraper :bookmark:")

# INTRO
st.markdown(
    """
    This app scrapes quotes from [Goodreads](https://www.goodreads.com/quotes) and returns a CSV file with the data. If you're an avid reader and a data enthusiast, then the Goodreads Quote Scraper is the perfect app for you! 🤓

## What is it? 🔎

Goodreads Quote Scraper is a powerful data science app built with Streamlit that allows you to scrape quotes from the popular book social networking site called Goodreads. With just a few clicks, you can select your favorite author, set the limit of pages to scrape, and voila! You'll get a CSV file with all the data you need!

## What does it do? 📈

Goodreads Quote Scraper fetches quotes, books, authors, likes, and tags associated with the quote, all within minutes! 🚀You can process thousands of rows in a matter of minutes. The app runs smoothly, so there are no restrictions or limitations, and you don't even need an API key!

## How does it work? 🔬

The app uses web scraping techniques to collect and extract data from Goodreads. It then processes the data and presents it in an easy-to-use format, making data analysis a breeze. You can use the data for research, analysis, or any other purposes you desire.

## Why should you use it?🎉

Goodreads Quote Scraper is a one-stop-shop for all your data analysis needs. Whether you're a bookworm, a data scientist, or both, the app is user-friendly, quick, and reliable. It saves you time and effort, and the CSV format makes it easy to export and use the data.

So, what are you waiting for? Try Goodreads Quote Scraper today and discover new insights from your favorite authors' quotes! 📚💻🔍

    """
)

st.markdown("---")

author = st.text_input(
    "Author", placeholder="Steven Erikson", key="author", help="Enter the author's name"
)

if author:
    author = author.lower()
    max_pages = get_max_pages(author)
    st.info(f"Total pages available for {author.capitalize()}: {max_pages}")


limit = st.number_input(
    "Number of Pages",
    min_value=1,
    max_value=500,
    value=1,
    key="limit",
    help="Enter the number of pages to scrape",
)

check_valid_btn = st.button(
    "Collect Quotes", key="check_author", help="Click to scrape quotes", type="primary"
)

if check_valid_btn:
    if len(author) >= 3 and is_author_valid(author):
        st.success("Author is Valid")
        max_pages = get_max_pages(author)

        st.markdown("---")

        if limit > max_pages:
            st.warning(
                f"We only found {max_pages} for pages {author.capitalize()}. Scraping {max_pages} pages instead."
            )
            limit = max_pages

        current_timestamp = pd.Timestamp.now().strftime("%Y_%m_%d_%H_%M_%S")

        scrape_quotes(author, limit, current_timestamp)

        st.markdown("---")

        author = author.replace(" ", "+")

        # post-processing
        with open(
            f"csvs/goodreads/quote-scraper/{author}_{current_timestamp}.csv",
            "r",
            encoding="utf-8",
            newline="",
        ) as quoteCSV:
            # check if "quote" row is empty, if yes, delete the entire row
            reader = csv.reader(quoteCSV)
            rows = list(reader)
            for row in rows:
                if row[0] == "":
                    rows.remove(row)

            # TODO: Add checkboxes for the following options before the collect quotes button and if checked, run the following code: 

            # TODO: Run Sentiment Analysis on the quotes

            # TODO: Before allowing download, sort the quotes by likes and group them by book alphabetically

            # TODO: Add 2-3 graphs to show the data


            # save the new csv
            with open(
                f"csvs/goodreads/quote-scraper/{author}_{current_timestamp}.csv",
                "w",
                encoding="utf-8",
                newline="",
            ) as quoteCSV:
                writer = csv.writer(quoteCSV)
                writer.writerows(rows)

        # DOWNLOAD BUTTON FOR THE GENERATED CSV
        with open(
            f"csvs/goodreads/quote-scraper/{author}_{current_timestamp}.csv", "rb"
        ) as quoteCSV:

            st.markdown("Preview of the first 5 quotes:")
            quotes_df = pd.read_csv(quoteCSV)
            st.dataframe(quotes_df.head(5))

            # download button
            st.download_button(
                label="Download All Quotes",
                data=quoteCSV,
                file_name=f"{author.capitalize()}.csv",
                mime="text/csv",
            )

    else:
        st.error("Author is not valid")


