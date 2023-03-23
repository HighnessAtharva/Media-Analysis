"""
AUTHOR: @highnessatharva<highnessatharva@gmail.com>

DATE: 2023-02-19

DESCRIPTION: Generate a report of your Steam library. The app returns a CSV file with the data. It takes a CSV file as input.  

API KEY: None 
"""


import json
import os
from functools import wraps

import pandas as pd
import streamlit as st


# #######################
# # DATA CLEANUP START #
# #######################
def cleanup_dataframe(games_df: pd.DataFrame):

    # drop id column
    games_df = games_df.drop("id", axis=1)

    # keep only year part of release_date
    games_df["release_date"] = pd.to_datetime(games_df["release_date"])
    games_df["release_date"] = games_df["release_date"].dt.year

    # rename release_dated to released
    games_df = games_df.rename(columns={"release_date": "released"})

    # create empty column genres
    games_df["genres"] = pd.Series(dtype=object)

    # create empty platform columns
    games_df["platforms"] = pd.Series(dtype=object)

    # shift the second last column to first position
    games_df.insert(0, "genres", games_df.pop("genres"))

    #############
    # GENRES
    #############

    # genre columns are columns 15-end
    genre_columns = games_df.columns[14:]

    # iterrate over each row
    for index, row in games_df.iterrows():
        to_add = [column for column in genre_columns if row[column] == "x"]
        games_df.at[index, "genres"] = ", ".join(to_add)

    # drop the genre_columns
    games_df = games_df.drop(genre_columns, axis=1)

    #############
    # PLATFORMS
    #############

    # platforms columns are mac, linux, windows, steamdeck
    my_platforms = ["mac", "linux", "win", "steam deck"]

    for index, row in games_df.iterrows():
        to_add = [column for column in my_platforms if row[column] == "x"]
        # fill - where platforms is NA
        if not to_add:
            to_add.append("-")
        games_df.at[index, "platforms"] = ", ".join(to_add)

    # drop the platform columns
    games_df = games_df.drop(my_platforms, axis=1)

    # move game column to first place
    games_df.insert(0, "game", games_df.pop("game"))

    # drop other unnecessary columns
    games_df = games_df.drop("wilsonscore", axis=1)
    games_df = games_df.drop("sdbrating", axis=1)

    # fill 0 where hours is NA
    games_df["hours"] = games_df["hours"].fillna(0)

    # fill "-" where metascore is NA
    games_df["metascore"] = games_df["metascore"].fillna(pd.NA)

    # # fill "-" where Userscore is NA
    games_df["userscore"] = games_df["userscore"].fillna(pd.NA)

    games_df.to_csv("csvs/steam/CHECKPOINT1.csv", index=False, encoding="utf-8")


# #######################
# # DATA ANALYSIS START #
# #######################
def add_seperator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        st.markdown("---")
        return result

    return wrapper


def total_games_count(games_df: pd.DataFrame):
    st.header("Total :green[Games] Played")
    st.markdown(f"## {len(games_df.index)}")


def genre_count(games_df: pd.DataFrame):
    genres = games_df["genres"].str.split(", ", expand=True).stack().unique()
    genres = [genre for genre in genres if genre != ""]
    st.header("Total :red[Genres]")
    st.markdown(f"## {len(genres)}")


def total_hours_played(games_df: pd.DataFrame):
    st.header("Total :blue[Hours] Played")
    st.markdown(f"## {games_df['hours'].sum()}")


# #########################
# FRONT-END SECTION START #
# #########################
st.set_page_config(
    page_title="Videogame Analysis",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title(":violet[Steam] VideoGame Analysis :video_game:")
st.warning(
    "Please Note: This part of the app is still under construction. Check back soon for updates! 🚧"
)
st.markdown(
    """
    Are you a gaming enthusiast who loves using Steam to keep track of your gaming history and discover new games to play? If so, then you're going to love the Steam Game Analysis Report tool. 🤩

## How it Works 
With the Steam Game Analysis Report, all you have to do is upload your Steam library export CSV file and let our tool do the rest. Our tool uses advanced data analysis techniques to generate statistical reports and provide you with in-depth insights that are not available on the Steam platform. 📈

## Features 

- **Analyze Your Gaming Habits:** Our tool provides detailed statistics on the games you've played, including the number of games played, average playtime, and total duration of games played.

- **Discover Your Gaming Preferences:** The Steam Game Analysis Report helps you understand your gaming preferences by providing information on the genres, publishers, and developers you've played the most.

- **Interactive Dashboards:** Our tool provides interactive dashboards that allow you to filter your data and explore your gaming patterns visually.

- **Personalized Recommendations:** Based on your gaming history, our tool provides personalized recommendations for games that you might enjoy, making it easy to discover your next favorite game. 

- **Time Period Graphs:** Our tool creates beautiful visualizations of your gaming history over time, allowing you to see your gaming habits and trends.

- **Awesome Visualizations:** The Steam Game Analysis Report tool also tells a story about your preferences and gaming habits through beautiful visualizations and interactive reports. Our tool generates graphs, charts, and other visualizations that make it easy to understand your gaming habits at a glance.

## How to Get Started 

Getting started with the Steam Game Analysis Report tool is easy. Visit [Steam Exporter]( https://www.lorenzostanco.com/lab/steam/) and enter your username. Download the CSV and upload it below. Our tool will take care of the rest! Whether you're a gaming enthusiast or just curious about your gaming habits, our app makes it easy for you to gain insights into your gaming library. So, what are you waiting for? Upload your CSV file and start analyzing your data today! 🕹️   
    """
)

st.write("---")

col1, col2 = st.columns(2, gap="large")
with col1:
    st.info(
        "Don't have a Steam library export file? No problem! You can download one from [Steam Exporter](https://www.lorenzostanco.com/lab/steam/)."
    )

with col2:
    st.info(
        "No Steam Account but still want to try out the app? No problem! You can download our sample CSV to try it out."
    )
    with open("pages/sample-csv/steam_export.csv", "rb") as steam_export:
        btn = st.download_button(
            label="Download Steam Libary Export File",
            data=steam_export,
            file_name="steam_export.csv",
            mime="text/csv",
            help="This is an example Steam Videogame Library export file. You can use this to test out the app.",
        )

st.write("---")


# FILE UPLOAD WIDGET
upload_file = st.file_uploader(
    label="Upload Steam Library Export File",
    type=["csv"],
    help="You can download one from [Steam Exporter](https://www.lorenzostanco.com/lab/steam/)",
    accept_multiple_files=False,
)

# VERIFY FILE -> GAMES
if upload_file is not None:
    games_df = pd.read_csv(upload_file, encoding="utf-8", header=0)
    cols_to_check = [
        "game",
        "id",
        "hours",
        "last_played",
        "metascore",
        "userscore",
        "userscore_count",
        "release_date",
        "win",
        "mac",
        "linux",
        "steam deck",
    ]
    if set(cols_to_check).issubset(set(games_df.columns)):

        st.success("Steam Library file uploaded successfully!")

        # check if file exists, if not, run cleanup function to create it
        if not os.path.isfile("csvs/steam/CHECKPOINT1.csv"):
            cleanup_dataframe(games_df)

        games_df = pd.read_csv("csvs/steam/CHECKPOINT1.csv", encoding="utf-8", header=0)

        st.write("---")

        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            total_games_count(games_df)
        with col2:
            genre_count(games_df)
        with col3:
            total_hours_played(games_df)

    else:
        st.error("Steam Export file is not valid. Please upload a valid export file.")
        st.stop()
