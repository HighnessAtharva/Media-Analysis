import calendar
import os
from datetime import datetime
from functools import wraps

import altair as alt
import numpy as np
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import urllib

# #######################
# # DATA CLEANUP START #
# #######################

def get_omdb_data(title, release_year, user_api_key):
    # get the API key from the environment variables

    API_KEY = user_api_key
    base_url = 'http://www.omdbapi.com/?'
    parameters = {'apikey': API_KEY, 't': title, 'y': release_year}
    params_encoded = urllib.parse.urlencode(parameters, quote_via=urllib.parse.quote, safe='')
    url = base_url + params_encoded

    response = requests.get(url).json()

    # Get the following data from OMDB
    # Runtime, Genre, Director, Rated, Language, Country, imdbRating, imdbVotes, BoxOffice
    runtime = response['Runtime']
    genre = response['Genre']
    director = response['Director']
    rated = response['Rated']
    language = response['Language']
    country = response['Country']
    imdb_rating = response['imdbRating']
    imdb_votes = response['imdbVotes']
    box_office = response['BoxOffice']
    return {'Runtime': runtime, 'Genre': genre, 'Director': director, 'Rated': rated, 'Language': language, 'Country': country, 'imdbRating': imdb_rating, 'imdbVotes': imdb_votes, 'BoxOffice': box_office}

def get_extend_dataframe_from_api(movie_df: pd.DataFrame, user_api_key):
    skipped_movies = []
    
    
    for idx, movie in enumerate(movie_df.iterrows(), start=1):
        try:
            # get omdb data for it and add it to the dataframe
            name = movie[1]['Name']
            year = int(movie[1]['Year'])
            
            omdb_data = get_omdb_data(name, year, user_api_key)

            # add new columns to the dataframe
            movie_df.loc[movie[0], 'Runtime'] = omdb_data['Runtime']
            movie_df.loc[movie[0], 'Genre'] = omdb_data['Genre']
            movie_df.loc[movie[0], 'Director'] = omdb_data['Director']
            movie_df.loc[movie[0], 'Rated'] = omdb_data['Rated']
            movie_df.loc[movie[0], 'Language'] = omdb_data['Language']
            movie_df.loc[movie[0], 'Country'] = omdb_data['Country']
            movie_df.loc[movie[0], 'imdbRating'] = omdb_data['imdbRating']
            movie_df.loc[movie[0], 'imdbVotes'] = omdb_data['imdbVotes']
            movie_df.loc[movie[0], 'BoxOffice'] = omdb_data['BoxOffice']

            st.write(f'{idx}. ✅ Added data for {name} ({year})')
                

        except Exception as e:
            name = movie[1]['Name']
            st.write(f'{idx}. ❌ Skipping {name} due to error: {e.__class__}')
            skipped_movies.append(name)

    # SAVE CHECKPOINT
    st.write(f"Total movies skipped: {len(skipped_movies)}")
    st.write(skipped_movies)
    st.write(f"Processed {len(movie_df)-len(skipped_movies)}. Writing to CSV file. Saving Checkpoint!")
    movie_df.to_csv('csvs/letterboxd/CHECKPOINT1.csv', index=False, encoding='utf-8')


def cleanup_dataframe(movie_df: pd.DataFrame):
    # replace all "NA" values with NaN
    movie_df = movie_df.replace('NA', pd.NA)

    # count all NaN values in each column
    print(f'Number of NaN values in each column: {movie_df.isna().sum()}')

    # keep only the first value of the runtime column (remove the 'min' part)
    movie_df['Runtime'] = movie_df['Runtime'].str.split(' ').str[0]

    # convert integer columns runtime, imdbRating, imdbVotes to int skip NaN values
    movie_df['Runtime'] = movie_df['Runtime'].astype(int, errors='ignore')
    movie_df['imdbRating'] = movie_df['imdbRating'].astype(int, errors='ignore')
    movie_df['imdbVotes'] = movie_df['imdbVotes'].astype(int, errors='ignore')


    # remove the '$' and ',' from the BoxOffice column and convert to int
    movie_df['BoxOffice'] = movie_df['BoxOffice'].str.replace('$', '')
    movie_df['BoxOffice'] = movie_df['BoxOffice'].str.replace(',', '')
    movie_df['BoxOffice'] = movie_df['BoxOffice'].astype(int, errors='ignore')


    # mutliply Rating by 2 to get a 10 point scale and convert to int
    movie_df['Rating'] = movie_df['Rating'] * 2
    movie_df['Rating'] = movie_df['Rating'].astype(int, errors='ignore')

    # remove None values from the Language column
    movie_df['Language'] = movie_df['Language'].str.replace('None', '')

    # check if csvs folder exists
    if not os.path.exists("csvs"):
        os.mkdir("csvs")
        if not os.path.exists("csvs/letterboxd"):
            os.mkdir("csvs/letterboxd")
            
    # SAVE CHECKPOINT
    movie_df.to_csv('csvs/letterboxd/CHECKPOINT2.csv', index=False, encoding='utf-8')
    
    
    
    
# PAGE CONFIG
st.set_page_config(
    page_title="Letterboxd Analysis",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# PAGE TITLE
st.title(":orange[Letterboxd] Movie Analysis :popcorn:")


# INTRO
st.markdown(
    """   
    # Letterboxd Movie Analysis Report 🎬

Are you a movie enthusiast who loves using Letterboxd to keep track of your movie watching history and discover new movies to watch? If so, then you're going to love the Letterboxd Movie Analysis Report tool. 🤩

## How it Works

With the Letterboxd Movie Analysis Report, all you have to do is upload your export CSV file from your Letterboxd account and let our tool do the rest. Our tool uses advanced data analysis techniques to generate statistical reports and provide you with in-depth insights that are not available on the Letterboxd platform. 📈

## Features

- **Analyze Your Movie Watching Data**: Our tool provides detailed statistics on the movies you've watched, including the number of movies watched, average rating, and total duration of movies watched.

- **Discover Your Movie Preferences**: The Letterboxd Movie Analysis Report helps you understand your movie preferences by providing information on the genres, directors, and actors you've watched the most.

- **Interactive Dashboards**: Our tool provides interactive dashboards that allow you to filter your data and explore your movie watching patterns visually. 

- **Personalized Recommendations**: Based on your movie watching history, our tool provides personalized recommendations for movies that you might enjoy, making it easy to discover your next favorite movie. 🍿

- **Storytelling Reports**: The Letterboxd Movie Analysis Report tool also tells a story about your preferences and movie watching habits through beautiful visualizations and interactive reports. 🎥

## How to Get Started

Getting started with the Letterboxd Movie Analysis Report tool is easy. Simply export your Letterboxd data as a CSV file and upload it to our tool. From there, our tool will analyze your data and provide you with a comprehensive report on your movie watching habits.

So why wait? Try out the Letterboxd Movie Analysis Report tool today and unlock the full potential of your movie watching history. 🚀

    """
)

st.write("---")

col1, col2 = st.columns(2, gap="large")
with col1:
    st.info(
        "Don't have a Letterboxd account? Create one [here](https://www.letterboxd.com/)."
    )

with col2:
    st.info("Don't have a Letterboxd export file? Get an example one below 👇🏻")

    col1, col2, col3 = st.columns([3,3,1], gap="small")
    with col1:
        with open("pages/letterboxd_diary.csv", "rb") as letterboxd_diary:
            btn = st.download_button(
                label="Download Diary Export Example",
                data=letterboxd_diary,
                file_name="letterboxd_diary.csv",
                mime="text/csv",
                help="This is an example Letterboxd export file. You can use this to test out the app.",
            )

    with col2:
        with open("pages/letterboxd_ratings.csv", "rb") as letterboxd_ratings:
            btn = st.download_button(
                label="Download Ratings Export Example",
                data=letterboxd_ratings,
                file_name="letterboxd_ratings.csv",
                mime="text/csv",
                help="This is an example Letterboxd export file. You can use this to test out the app.",
            )

    with col3:
        st.write("")



st.write("---")
# FILE UPLOAD WIDGET
diary_file = st.file_uploader(
    label="Upload Letterboxd Diary Export File",
    type=["csv"],
    help="Letterboxd Account -> Settings -> Import & Export",
    accept_multiple_files=False,
)

ratings_file = st.file_uploader(
    label="Upload Letterboxd Ratings Export File",
    type=["csv"],
    help="Letterboxd Account -> Settings -> Import & Export",
    accept_multiple_files=False,
)

user_api_key=st.text_input("Enter your OMBD API key here", placeholder="Eight lettered OMDB API key", help="You can get your OMDB API key from here: http://www.omdbapi.com/apikey.aspx")



# TODO: ADD A INPUT BOX FOR USERS TO ENTER THEIR OMBD KEY HERE AND MAKE ONE REQUEST TO CHECK ITS AUTHENTICITY. PROGRESS ONLY IF KEY IS VALID. MENTION THAT WE DO NOT STORE THE KEY IN ANY WAY. REQUEST LIMIT PER DAY IS 1000. PASS THAT KEY TI get_extend_dataframe_from_api function instead of using your own key.

if diary_file is not None:
    # VERIFY FILE -> DIARY
    diary_df = pd.read_csv(diary_file, encoding="utf-8", header=0)
    cols_to_check = ["Date","Name","Year","Letterboxd URI","Rating","Watched Date"]
    if set(cols_to_check).issubset(set(diary_df.columns)):   
        st.success("Diary file uploaded successfully!")
        diary_df = diary_df[cols_to_check]

    else: 
        st.error("Diary file is not valid. Please upload a valid Letterboxd diary export file.")
        st.stop()

if ratings_file is not None:
    # VERIFY FILE -> RATINGS
    ratings_df = pd.read_csv(ratings_file, encoding="utf-8", header=0)
    cols_to_check = ["Date","Name","Year","Rating"]
    if set(cols_to_check).issubset(set(ratings_df.columns)): 
        st.success("Ratings file uploaded successfully!")
        ratings_df = ratings_df[cols_to_check]

    else:
        st.error("Ratings file is not valid. Please upload a valid Letterboxd ratings export file.")
        st.stop()


   

if len(user_api_key) == 8:
    KEY_VERIFICATION_PASSED = False
    # get the movie name and year from the first row of the dataframe
    name = 'Reservoir Dogs'
    year = 1992
    base_url = 'http://www.omdbapi.com/?'
    parameters = {'apikey': user_api_key, 't': name, 'y': year}
    params_encoded = urllib.parse.urlencode(parameters, quote_via=urllib.parse.quote, safe='')
    url = base_url + params_encoded

    response = requests.get(url).json()

    # check status code of the response
    if response['Response'] == 'True':
        st.success("This is a valid OMDB API Key.")
        KEY_VERIFICATION_PASSED = True
    else:
        st.error("This is not a valid OMDB API Key.")
         
else:
    st.error("Please enter a valid OMBD API key to continue.")
    st.stop()


if KEY_VERIFICATION_PASSED and diary_file is not None and ratings_file is not None:
    # MERGE DATAFRAMES
    movie_df = ratings_df
    # add column to movie_df for Watched Date
    movie_df["Watched Date"] = ""


    # check if ratings_df['Name'] is in diary_df['Name'] and value matches and if so then add diary_df['Watched Date'] to movie_df['Watched Date']
    for index, row in movie_df.iterrows():
        if row['Name'] in diary_df['Name'].values:
            movie_df.loc[index, 'Watched Date'] = diary_df.loc[diary_df['Name'] == row['Name'], 'Watched Date'].values[0]

    # drop the Date column from movie_df
    movie_df = movie_df.drop(columns=['Date'])
    
    # check if csvs/Letterboxd folder exists and file CHECKPOINT1.csv exists, if not then run cleanup_dataframe
    if not os.path.exists("csvs/Letterboxd/CHECKPOINT1.csv"):
        get_extend_dataframe_from_api(movie_df, user_api_key)

    if not os.path.exists("csvs/Letterboxd/CHECKPOINT2.csv"):
        cleanup_dataframe(movie_df)

    movie_df = pd.read_csv(
        "csvs/Letterboxd/CHECKPOINT2.csv", encoding="utf-8", header=0
    )

    st.header("Data Preview")
    # st.dataframe(movie_df)
    st.markdown("---")
    
# TODO: START DATA ANALYSIS HERE

# #######################
# # DATA ANALYSIS START #
# #######################


# def total_movies_watched(movie_df: pd.DataFrame):
#     total_movies_watched = len(movie_df)
#     print(tabulate([['Total movies watched', total_movies_watched]], headers=['Metric', 'Value'], tablefmt='fancy_grid'))


# def top_10_movies_by_rating(movie_df: pd.DataFrame):
#     top_10_movies_by_rating = movie_df.sort_values(by=['Rating'], ascending=False)
#     print(f'Top 10 movies in {YEAR}')
#     print(tabulate(tabular_data=top_10_movies_by_rating[['Name', 'Rating']].head(10).values, headers=['Movie', 'Your Rating'], tablefmt='fancy_grid'))


# def top_10_movies_by_runtime(movie_df):
#     top_10_movies_by_runtime = movie_df.sort_values(by=['Runtime'], ascending=False)
#     print(f'Top 10 movies by runtime in {YEAR}')
#     print(tabulate(tabular_data=top_10_movies_by_runtime[['Name', 'Runtime']].head(10).values, headers=['Movie', 'Runtime (mins)'], tablefmt='fancy_grid'))


# def top_10_movies_by_imdb_rating(movie_df):
#     top_10_movies_by_imdb_rating = movie_df.sort_values(by=['imdbRating'], ascending=False)
#     print(f'Top 10 movies by IMDB rating in {YEAR}')
#     print(tabulate(tabular_data=top_10_movies_by_imdb_rating[['Name', 'imdbRating']].head(10).values, headers=['Movie', 'IMDB Rating'], tablefmt='fancy_grid'))


# def top_10_movies_by_imdb_votes(movie_df):
#     # remove commas from imdbVotes column
#     movie_df['imdbVotes'] = movie_df['imdbVotes'].str.replace(',', '')

#     # convert imdbVotes to numeric
#     movie_df['imdbVotes'] = pd.to_numeric(movie_df['imdbVotes'], errors='coerce')

#     # divide imdbVotes by 1000 to get the number of thousands of votes
#     movie_df['imdbVotes'] = (movie_df['imdbVotes'] / 1000).round(0)


#     top_10_movies_by_imdb_votes = movie_df.sort_values(by=['imdbVotes'], ascending=False)

#     # append 'K' to the end of the imdbVotes column
#     top_10_movies_by_imdb_votes['imdbVotes'] = top_10_movies_by_imdb_votes['imdbVotes'].astype(str) + ' K'

#     # remove .0 from the end of the imdbVotes column
#     top_10_movies_by_imdb_votes['imdbVotes'] = top_10_movies_by_imdb_votes['imdbVotes'].str.replace('.0 K', ' K')


#     print(f'Top 10 movies by IMDB votes in {YEAR}')
#     print(tabulate(tabular_data=top_10_movies_by_imdb_votes[['Name', 'imdbVotes']].head(10).values, headers=['Movie', 'IMDB Votes'], tablefmt='fancy_grid'))


# def top_10_movies_by_box_office(movie_df):
#     top_10_movies_by_box_office = movie_df.sort_values(by=['BoxOffice'], ascending=False)
#     # convert BoxOffice to millions and round to 2 decimal places and prefix with $ sign
#     top_10_movies_by_box_office['BoxOffice'] = (top_10_movies_by_box_office['BoxOffice'] / 1000000).round(2)
#     top_10_movies_by_box_office['BoxOffice'] = "$" + top_10_movies_by_box_office['BoxOffice'].astype(str) + ' M'
#     print(f'Top 10 movies by box office in {YEAR}')
#     print(tabulate(top_10_movies_by_box_office[['Name', 'BoxOffice']].head(10), headers = 'keys', tablefmt = 'fancy_grid', showindex=False))



# def top_10_movies_by_genre(movie_df):
#     # seperate genres into a list
#     movie_df['Genre'] = movie_df['Genre'].str.split(', ')
#     # explode the list into multiple rows
#     movie_df = movie_df.explode('Genre')
#     # group by genre and count the number of movies in each genre
#     top_10_movies_by_genre = movie_df.groupby('Genre').count().sort_values(by=['Name'], ascending=False)
#     print(f'Top 10 movies by genre in {YEAR}')
#     print(tabulate(tabular_data=top_10_movies_by_genre[['Name']].head(10), headers = ['Genre', 'Count'], tablefmt = 'fancy_grid', showindex=True))



# def top_10_movies_by_director(movie_df):
#     top_10_movies_by_director = movie_df.groupby('Director').count().sort_values(by=['Name'], ascending=False)
#     print(f'Top 10 movies by director in {YEAR}')
#     print(tabulate(tabular_data=top_10_movies_by_director[['Name']].head(10), headers = ['Director', 'Count'], tablefmt = 'fancy_grid', showindex=True))


# def top_10_movies_by_language(movie_df):
#     movie_df['Language'] = movie_df['Language'].str.split(', ').str[0]
#     top_10_movies_by_language = movie_df.groupby('Language').count().sort_values(by=['Name'], ascending=False)
#     print(f'Top 10 movies by language in {YEAR}')
#     print(tabulate(tabular_data=top_10_movies_by_language[['Name']].head(10), headers = ['Language', 'Count'], tablefmt = 'fancy_grid', showindex=True))


# def top_10_movies_by_country(movie_df):
#     movie_df['Country'] = movie_df['Country'].str.split(', ').str[0]
#     top_10_movies_by_country = movie_df.groupby('Country').count().sort_values(by=['Name'], ascending=False)
#     print(f'Top 10 movies by country in {YEAR}')
#     print(tabulate(tabular_data=top_10_movies_by_country[['Name']].head(10), headers = ['Country', 'Count'], tablefmt = 'fancy_grid', showindex=True))



# def first_and_last_movie_watched(movie_df):
#     first_movie_watched = movie_df.sort_values(by=['Watched Date'], ascending=True)
#     first=first_movie_watched["Name"].head(1).to_string(index=False)
#     first_date=first_movie_watched["Watched Date"].head(1).to_string(index=False)

#     last_movie_watched = movie_df.sort_values(by=['Watched Date'], ascending=False)
#     last=last_movie_watched["Name"].head(1).to_string(index=False)
#     last_date=last_movie_watched["Watched Date"].head(1).to_string(index=False)

#     print(tabulate(tabular_data=[['First Movie Watched', first, first_date], ['Last Movie Watched', last, last_date]], headers = ['#', 'Movie', 'Watched Date'], tablefmt = 'fancy_grid', showindex=False))


# def top_10_box_office_flops(movie_df):
#     top_10_box_office_flops = movie_df.sort_values(by=['BoxOffice'], ascending=True)
#     # convert BoxOffice to millions and round to 2 decimal places and prefix with $ sign
#     top_10_box_office_flops['BoxOffice'] = top_10_box_office_flops['BoxOffice']
#     top_10_box_office_flops['BoxOffice'] = "$" + top_10_box_office_flops['BoxOffice'].astype(str)
#     print(f'Top 10 box office flops in {YEAR}')
#     print(tabulate(tabular_data=top_10_box_office_flops[['Name', 'BoxOffice']].head(10), headers = 'keys', tablefmt = 'fancy_grid', showindex=False))


# def top_10_imdb_rating_flops(movie_df):
#     top_10_imdb_rating_flops = movie_df.sort_values(by=['imdbRating'], ascending=True)
#     print(f'Top 10 IMDB rating flops in {YEAR}')
#     print(tabulate(tabular_data=top_10_imdb_rating_flops[['Name', 'imdbRating']].head(10), headers = 'keys', tablefmt = 'fancy_grid', showindex=False))


# def top_10_worst_movies_by_your_rating(movie_df):
#     top_10_worst_movies_by_your_rating = movie_df.sort_values(by=['Rating'], ascending=True)
#     print(f'Top 10 worst movies by your rating in {YEAR}')
#     print(tabulate(tabular_data=top_10_worst_movies_by_your_rating[['Name', 'Rating']].head(10), headers = 'keys', tablefmt = 'fancy_grid', showindex=False))


# def shortest_and_longest_movie_watched(movie_df):
#     shortest_movie_watched = movie_df.sort_values(by=['Runtime'], ascending=True)
#     shortest=shortest_movie_watched["Name"].head(1).to_string(index=False)
#     shortest_runtime=shortest_movie_watched["Runtime"].head(1).to_string(index=False)

#     longest_movie_watched = movie_df.sort_values(by=['Runtime'], ascending=False)
#     longest=longest_movie_watched["Name"].head(1).to_string(index=False)
#     longest_runtime=longest_movie_watched["Runtime"].head(1).to_string(index=False)
#     print(tabulate(tabular_data=[['Shortest Movie Watched', shortest, shortest_runtime], ['Longest Movie Watched', longest, longest_runtime]], headers = ['#', 'Movie', 'Runtime'], tablefmt = 'fancy_grid', showindex=False))


# def total_time_watched(movie_df):
#     total_minutes_watched = movie_df['Runtime'].sum()
#     # convert minutes to hours and minutes
#     hours, minutes = divmod(total_minutes_watched, 60)
#     hours, minutes = int(hours), int(minutes)
#     print(tabulate(tabular_data=[['Total Hours Watched', f'{hours} hours and {minutes} minutes']], headers = ['#', 'Runtime Sum'], tablefmt = 'fancy_grid', showindex=False))


# def average_movie_rating(movie_df):
#     average_movie_rating = movie_df['Rating'].mean().round(2)
#     print(tabulate(tabular_data=[['Average Movie Rating', average_movie_rating]], headers = ['#', 'Rating'], tablefmt = 'fancy_grid', showindex=False))


# def average_movie_runtime(movie_df):
#     average_movie_runtime = movie_df['Runtime'].mean()
#     # convert minutes to hours and minutes
#     hours, minutes = divmod(average_movie_runtime, 60)
#     hours, minutes = int(hours), int(minutes)
#     print(tabulate(tabular_data=[['Average Movie Runtime', f'{hours} hours and {minutes} minutes']], headers = ['#', 'Runtime'], tablefmt = 'fancy_grid', showindex=False))


# def oldest_release_date(movie_df):
#     oldest_release_date = movie_df.sort_values(by=['Year'], ascending=True)
#     oldest=oldest_release_date["Name"].head(1).to_string(index=False)
#     oldest_release=oldest_release_date["Year"].head(1).to_string(index=False)
#     print(tabulate(tabular_data=[['Oldest Release Date', oldest, oldest_release]], headers = ['#', 'Movie', 'Release Date'], tablefmt = 'fancy_grid', showindex=False))


# def adult_movies_watched(movie_df):
#     adult_movies_watched = movie_df[movie_df['Rated'] == 'R']
#     print(f'Adult movies watched in {YEAR}: {adult_movies_watched["Name"].count()}')
#     print(tabulate(tabular_data=adult_movies_watched[['Name', 'Rated']], headers = 'keys', tablefmt = 'fancy_grid', showindex=False))


# def highly_rated_but_imdb_low(movie_df):
#     # check the imdb score for highly rated movies (8.0+) but low Rating (4.0-)
#     highly_rated_but_imdb_low = movie_df[(movie_df['imdbRating'] >= 8.0) & (movie_df['Rating'] <= 4.0)]
#     print(f'Highly rated by audiences but low Rating by you in {YEAR}: {highly_rated_but_imdb_low["Name"].count()}')
#     print(tabulate(tabular_data=highly_rated_but_imdb_low[['Name', 'imdbRating', 'Rating']], headers = 'keys', tablefmt = 'fancy_grid', showindex=False))



# def lowly_rated_but_imdb_high(movie_df):
#     # check the imdb score for lowly rated movies (4.0-) but highly rated (8.0+) by you
#     lowly_rated_but_imdb_high = movie_df[(movie_df['imdbRating'] <= 4.0) & (movie_df['Rating'] >= 8.0)]
#     print(f'Lowly rated by audiences but highly rated by you in {YEAR}: {lowly_rated_but_imdb_high["Name"].count()}')
#     print(tabulate(tabular_data=lowly_rated_but_imdb_high[['Name', 'imdbRating', 'Rating']], headers = 'keys', tablefmt = 'fancy_grid', showindex=False))


# # TODO: Function needs to be tested
# def longest_watch_streak(movie_df):
#     from datetime import timedelta
#     # sort by date
#     movie_df = movie_df.sort_values(by=['Watched Date'], ascending=True)
#     # create a new column with the difference between the current date and the previous date
#     movie_df['Watched Date'] = pd.to_datetime(movie_df['Watched Date'])
#     movie_df['streak'] = movie_df['Watched Date'].diff()

#     # select date column where streak is max
#     longest_streak = movie_df.loc[movie_df['streak'].idxmax()]
#     jump_days = longest_streak['streak'].days+1

#     # go back jump_day rows to get the movie before the longest streak
#     movie_before_streak = movie_df.iloc[movie_df.index.get_loc(longest_streak.name) - jump_days]

#     # get the date of the movie before the longest streak
#     start = movie_before_streak['Watched Date'].date()

#     # add the jump_days to the start date to get the end date
#     end = start + timedelta(days=jump_days)
#     end = end.strftime('%Y-%m-%d')
#     print(tabulate(tabular_data=[['Longest Watch Streak', f'{jump_days} days', start, end]], headers = ['#', 'Days', 'Start', 'End'], tablefmt = 'fancy_grid', showindex=False))


# def most_watched_month(movie_df):
#     pass

# def least_watched_month(movie_df):
#     pass



# # LOAD/PROCESS CHECKPOINT 1
# if os.path.isfile('CHECKPOINT1.csv'):
#     movie_df = pd.read_csv('CHECKPOINT1.csv', encoding='utf-8')
#     print(f'Loaded checkpoint file #1. Continuing from {len(movie_df)} movies.')
# else:
#     get_extend_dataframe_from_api(movie_df)

# # LOAD/PROCESS CHECKPOINT 2
# if os.path.isfile('CHECKPOINT2.csv'):
#     movie_df = pd.read_csv('CHECKPOINT2.csv', encoding='utf-8')
#     print(f'Loaded checkpoint file #2. Continuing from {len(movie_df)} movies.')
# else:
#     cleanup_dataframe(movie_df)


# total_movies_watched(movie_df)
# total_time_watched(movie_df)
# average_movie_rating(movie_df)
# adult_movies_watched(movie_df)
# average_movie_runtime(movie_df)
# longest_watch_streak(movie_df)
# top_10_movies_by_rating(movie_df)
# top_10_movies_by_runtime(movie_df)
# top_10_movies_by_imdb_rating(movie_df)
# top_10_movies_by_imdb_votes(movie_df)
# top_10_movies_by_box_office(movie_df)
# top_10_movies_by_genre(movie_df)
# top_10_movies_by_director(movie_df)
# top_10_movies_by_language(movie_df)
# top_10_movies_by_country(movie_df)
# first_and_last_movie_watched(movie_df)
# top_10_box_office_flops(movie_df)
# top_10_imdb_rating_flops(movie_df)
# top_10_worst_movies_by_your_rating(movie_df)
# shortest_and_longest_movie_watched(movie_df)
# oldest_release_date(movie_df)
# highly_rated_but_imdb_low(movie_df)
# lowly_rated_but_imdb_high(movie_df)
