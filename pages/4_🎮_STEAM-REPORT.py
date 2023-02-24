# # ALL DATA OBTAINED FROM - https://www.lorenzostanco.com/lab/steam/

import pandas as pd
import json
import os

import streamlit as st

st.set_page_config(
    page_title="Videogame Analysis",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title(":violet[Steam] VideoGame Analysis :video_game:")
st.warning("Please Note: This part of the app is still under construction. Check back soon for updates! 🚧")
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

# #######################
# # DATA CLEANUP START #
# #######################

# def cleanup_dataframe(games_df: pd.DataFrame):

#     # drop id column
#     games_df = games_df.drop('id', axis=1)

#     # keep only year part of release_date
#     games_df['release_date'] = pd.to_datetime(games_df['release_date'])
#     games_df['release_date'] = games_df['release_date'].dt.year

#     # rename release_dated to released
#     games_df = games_df.rename(columns={'release_date': 'released'})

#     # create empty column genres
#     games_df['genres'] = pd.Series(dtype=object)

#     # create empty platform columns
#     games_df['platforms'] = pd.Series(dtype=object)

#     # shift the second last column to first position
#     games_df.insert(0, 'genres', games_df.pop('genres'))
#     games_df.insert(1, 'Year', games_df.pop('Year'))

#     # rename Year column to last_played
#     games_df = games_df.rename(columns={'Year': 'last_played'})

#     #############
#     # GENRES
#     #############

#     # genre columns are columns 15-end
#     genre_columns =  games_df.columns[14:]

#     # iterrate over each row
#     for index, row in games_df.iterrows():
#         to_add = [column for column in genre_columns if row[column] == 'x']
#         games_df.at[index, 'genres'] = ', '.join(to_add)

#     # drop the genre_columns
#     games_df = games_df.drop(genre_columns, axis=1)


#     #############
#     # PLATFORMS
#     #############

#     # platforms columns are mac, linux, windows, steamdeck
#     my_platforms = ['mac', 'linux', 'win', 'steam deck']

#     for index, row in games_df.iterrows():
#         to_add = [column for column in my_platforms if row[column] == 'x']
#         # fill - where platforms is NA
#         if not to_add:
#             to_add.append('-')
#         games_df.at[index, 'platforms'] = ', '.join(to_add)


#     # drop the platform columns
#     games_df = games_df.drop(my_platforms, axis=1)

#     # move game column to first place
#     games_df.insert(0, 'game', games_df.pop('game'))

#     # drop other unnecessary columns
#     games_df = games_df.drop('wilsonscore', axis=1)
#     games_df = games_df.drop('sdbrating', axis=1)


#     # fill 0 where hours is NA
#     games_df['hours'] = games_df['hours'].fillna(0)

#     # fill "-" where metascore is NA
#     games_df['metascore'] = games_df['metascore'].fillna('-')

#     # # fill "-" where Userscore is NA
#     games_df['userscore'] = games_df['userscore'].fillna('-')

#     print(games_df)
#     # print(games_df.loc[1])
#     # print(games_df.loc[2])
#     games_df.to_csv('CHECKPOINT1.csv', index=False, encoding='utf-8')


# #######################
# # DATA ANALYSIS START #
# #######################

# def pretty_printer():
#     print("""
#           ----------------8<-------------[ Annual Videogame Report ]------------------
#           """)


# YEAR = 2022
# games_df = pd.read_csv('steam_export.csv', encoding='utf-8', header=0)

# # get rid of rows where 'last_played' column does not contain '2022'
# games_df['last_played']=pd.to_datetime(games_df['last_played'])
# games_df['Year'] = games_df['last_played'].dt.year
# games_df = games_df[games_df['Year'] == YEAR]

# # remove last_played column
# games_df = games_df.drop('last_played', axis=1)


# # LOAD/PROCESS CHECKPOINT 1
# if os.path.isfile('CHECKPOINT1.csv'):
#     games_df = pd.read_csv('CHECKPOINT1.csv', encoding='utf-8')
#     print(f'Loaded checkpoint file #1. Continuing from {len(games_df)} games.')
# else:
#     cleanup_dataframe(games_df)
