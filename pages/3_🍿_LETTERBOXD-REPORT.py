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
    API_KEY = user_api_key
    base_url = "http://www.omdbapi.com/?"
    parameters = {"apikey": API_KEY, "t": title, "y": release_year}
    # params_encoded = urllib.parse.urlencode(parameters)
    # url = base_url + params_encoded
    response = requests.get(base_url, params=parameters).json()

    # Get the following data from OMDB
    # Runtime, Genre, Director, Rated, Language, Country, imdbRating, imdbVotes, BoxOffice
    runtime = response["Runtime"]
    genre = response["Genre"]
    director = response["Director"]
    rated = response["Rated"]
    language = response["Language"]
    country = response["Country"]
    imdb_rating = response["imdbRating"]
    imdb_votes = response["imdbVotes"]
    box_office = response["BoxOffice"]
    return {
        "Runtime": runtime,
        "Genre": genre,
        "Director": director,
        "Rated": rated,
        "Language": language,
        "Country": country,
        "imdbRating": imdb_rating,
        "imdbVotes": imdb_votes,
        "BoxOffice": box_office,
    }


def get_extend_dataframe_from_api(movie_df: pd.DataFrame, user_api_key):
    skipped_movies = []

    col1, col2 = st.columns(2)

    for idx, movie in enumerate(movie_df.iterrows(), start=1):
        try:
            # get omdb data for it and add it to the dataframe
            name = movie[1]["Name"]
            year = int(movie[1]["Year"])

            omdb_data = get_omdb_data(name, year, user_api_key)

            # add new columns to the dataframe
            movie_df.loc[movie[0], "Runtime"] = omdb_data["Runtime"]
            movie_df.loc[movie[0], "Genre"] = omdb_data["Genre"]
            movie_df.loc[movie[0], "Director"] = omdb_data["Director"]
            movie_df.loc[movie[0], "Rated"] = omdb_data["Rated"]
            movie_df.loc[movie[0], "Language"] = omdb_data["Language"]
            movie_df.loc[movie[0], "Country"] = omdb_data["Country"]
            movie_df.loc[movie[0], "imdbRating"] = omdb_data["imdbRating"]
            movie_df.loc[movie[0], "imdbVotes"] = omdb_data["imdbVotes"]
            movie_df.loc[movie[0], "BoxOffice"] = omdb_data["BoxOffice"]

            if idx % 2 != 0:
                with col1:
                    st.write(f"{idx}. ✅ Added data for {name} ({year})")
            else:
                with col2:
                    st.write(f"{idx}. ✅ Added data for {name} ({year})")

        except Exception as e:
            name = movie[1]["Name"]
            st.write(f"{idx}. ❌ Skipping {name} due to error: {e.__class__}")
            skipped_movies.append(name)

    # SAVE CHECKPOINT
    st.info(f"Total movies skipped: {len(skipped_movies)}")
    # st.write(skipped_movies)
    st.success(
        f"Processed {len(movie_df)-len(skipped_movies)}. Writing to CSV file. Saving Checkpoint!"
    )
    movie_df.to_csv("csvs/letterboxd/CHECKPOINT1.csv", index=False, encoding="utf-8")


def cleanup_dataframe(movie_df: pd.DataFrame):
    # rename columns
    movie_df = movie_df.rename(
        columns={
            "Name": "Movie",
            "Rating": "Your Rating",
            "imdbRating": "IMDB Rating",
            "imdbVotes": "IMDB Votes",
            "Runtime": "Runtime (min)",
        }
    )

    # replace all "NA" values with NaN
    movie_df = movie_df.replace("NA", pd.NA)

    # keep only the first value of the runtime column (remove the 'min' part)
    movie_df["Runtime (min)"] = movie_df["Runtime (min)"].str.split(" ").str[0]

    # convert integer columns runtime, imdbRating, imdbVotes to int skip NaN values
    movie_df["Runtime (min)"] = movie_df["Runtime (min)"].astype(int, errors="ignore")
    movie_df["IMDB Rating"] = movie_df["IMDB Rating"].astype(int, errors="ignore")
    movie_df["IMDB Votes"] = movie_df["IMDB Votes"].astype(int, errors="ignore")

    # remove the '$' and ',' from the BoxOffice column and convert to int
    movie_df["BoxOffice"] = movie_df["BoxOffice"].str.replace("$", "")
    movie_df["BoxOffice"] = movie_df["BoxOffice"].str.replace(",", "")
    movie_df["BoxOffice"] = movie_df["BoxOffice"].astype(int, errors="ignore")

    # mutliply Rating by 2 to get a 10 point scale and convert to int
    movie_df["Your Rating"] = movie_df["Your Rating"] * 2
    movie_df["Your Rating"] = movie_df["Your Rating"].astype(int, errors="ignore")

    # remove None values from the Language column
    movie_df["Language"] = movie_df["Language"].str.replace("None", "")

    # remove commas from Year, Runtime, imdbVotes, BoxOffice
    movie_df["Year"] = movie_df["Year"].astype(str).str.replace(",", "")
    movie_df["Runtime (min)"] = (
        movie_df["Runtime (min)"].astype(str).str.replace(",", "")
    )
    movie_df["IMDB Votes"] = movie_df["IMDB Votes"].astype(str).str.replace(",", "")
    movie_df["BoxOffice"] = movie_df["BoxOffice"].astype(str).str.replace(",", "")

    # convert Year, Runtime, imdbVotes, BoxOffice to numeric
    movie_df["Year"] = pd.to_numeric(movie_df["Year"], errors="coerce")
    movie_df["Runtime (min)"] = pd.to_numeric(
        movie_df["Runtime (min)"], errors="coerce"
    )
    movie_df["IMDB Votes"] = pd.to_numeric(movie_df["IMDB Votes"], errors="coerce")
    movie_df["BoxOffice"] = pd.to_numeric(movie_df["BoxOffice"], errors="coerce")

    # check if csvs folder exists
    if not os.path.exists("csvs"):
        os.mkdir("csvs")
        if not os.path.exists("csvs/letterboxd"):
            os.mkdir("csvs/letterboxd")

    # SAVE CHECKPOINT
    movie_df.to_csv("csvs/letterboxd/CHECKPOINT2.csv", index=False, encoding="utf-8")


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

@add_seperator
def total_movies_watched(movie_df: pd.DataFrame):
    st.header("Total Movies")
    st.markdown(f"### {len(movie_df)}")


def best_movies_by_rating(movie_df: pd.DataFrame):
    movie_df = movie_df.sort_values(
        by=["Your Rating", "IMDB Rating", "IMDB Votes"], ascending=False
    )
    movie_df = movie_df.set_index("Movie")
    st.header("Your Favorite Movies")
    st.dataframe(
        movie_df.head(10)[["Your Rating", "IMDB Rating", "IMDB Votes"]],
        use_container_width=True,
    )


def worst_movies_by_rating(movie_df: pd.DataFrame):
    movie_df = movie_df.sort_values(
        by=["Your Rating", "IMDB Rating", "IMDB Votes"], ascending=True
    )
    movie_df = movie_df.set_index("Movie")
    st.header("Your Least Favorite Movies")
    st.dataframe(
        movie_df.head(10)[["Your Rating", "IMDB Rating", "IMDB Votes"]],
        use_container_width=True,
    )


def longest_movies_by_runtime(movie_df: pd.DataFrame):
    movie_df = movie_df.sort_values(by=["Runtime (min)"], ascending=False)
    movie_df = movie_df.set_index("Movie")
    st.header("Longest Runtime Movies")
    st.dataframe(movie_df.head(10)[["Runtime (min)"]], use_container_width=True)


def shortest_movies_by_runtime(movie_df: pd.DataFrame):
    movie_df = movie_df.sort_values(by=["Runtime (min)"], ascending=True)
    movie_df = movie_df.set_index("Movie")
    st.header("Shortest Runtime Movies")
    st.dataframe(movie_df.head(10)[["Runtime (min)"]], use_container_width=True)


def best_movies_by_imdb_rating(movie_df: pd.DataFrame):
    movie_df = movie_df.sort_values(by=["IMDB Rating", "IMDB Votes"], ascending=False)
    movie_df = movie_df.set_index("Movie")
    st.header("IMDBs Favorite Movies")
    st.dataframe(
        movie_df.head(10)[["IMDB Rating", "IMDB Votes"]], use_container_width=True
    )


def worst_movies_by_imdb_rating(movie_df: pd.DataFrame):
    movie_df = movie_df.sort_values(by=["IMDB Rating", "IMDB Votes"], ascending=True)
    movie_df = movie_df.set_index("Movie")
    st.header("IMDBs Least Favorite Movies")
    st.dataframe(
        movie_df.head(10)[["IMDB Rating", "IMDB Votes"]], use_container_width=True
    )


def most_popular_movies(movie_df: pd.DataFrame):
    movie_df = movie_df.sort_values(by=["IMDB Votes"], ascending=False)
    movie_df["IMDB Votes"] = (movie_df["IMDB Votes"] / 1000).round(0)
    movie_df["IMDB Votes"] = movie_df["IMDB Votes"].astype(str) + "K"
    movie_df["IMDB Votes"] = movie_df["IMDB Votes"].str.replace(".0K", " K")
    movie_df = movie_df.rename(
        columns={"IMDB Votes": "IMDB Votes"}
    )  # Renaming the column
    movie_df = movie_df.set_index("Movie")
    st.header("Most Popular Movies")
    st.dataframe(movie_df.head(10)[["IMDB Votes"]], use_container_width=True)


def most_watched_directors(movie_df: pd.DataFrame):
    # get the count of most watched directors
    director_df = (
        movie_df["Director"]
        .value_counts()
        .rename_axis("Director")
        .reset_index(name="Count")
    )
    director_df = director_df.sort_values(by=["Count"], ascending=False)
    director_df = director_df.set_index("Director")
    director_df = director_df.rename(columns={"Count": "Number of Movies Watched"})
    st.header("Most Watched Directors")
    st.dataframe(director_df.head(10), use_container_width=True)


def highest_grossing_movies(movie_df: pd.DataFrame):
    movie_df = movie_df.sort_values(by=["BoxOffice"], ascending=False)
    movie_df["BoxOffice"] = (movie_df["BoxOffice"] / 1000000).round(2)
    movie_df["BoxOffice"] = "$" + movie_df["BoxOffice"].astype(str) + " M"
    movie_df = movie_df.set_index("Movie")
    st.header("Highest Grossing Movies")
    st.dataframe(movie_df.head(10)[["BoxOffice"]], use_container_width=True)


def lowest_grossing_movies(movie_df: pd.DataFrame):
    movie_df = movie_df.sort_values(by=["BoxOffice"], ascending=True)
    movie_df["BoxOffice"] = "$" + movie_df["BoxOffice"].astype(str)
    # remove last 2 characters
    movie_df["BoxOffice"] = movie_df["BoxOffice"].str[:-2]
    movie_df = movie_df.set_index("Movie")
    st.header("Lowest Grossing Movies")
    st.dataframe(movie_df.head(10)[["BoxOffice"]], use_container_width=True)

@add_seperator
def director_films_rating_ranked(movie_df: pd.DataFrame, director):
    director_df = movie_df[movie_df["Director"] == director]
    director_df = director_df.sort_values(
        by=["Your Rating", "IMDB Rating"], ascending=False
    )
    director_df = director_df.set_index("Movie")
    fig = px.bar(
        director_df,
        x=director_df.index,
        y="Your Rating",
        color="Your Rating",
        title=f"{director}'s Movies Ranked By Your Rating",
        color_continuous_scale=px.colors.sequential.Greens,
    )
    st.plotly_chart(fig, use_container_width=True)


def pie_chart_genre(movie_df: pd.DataFrame):
    # seperate genres into a list
    movie_df["Genre"] = movie_df["Genre"].str.split(", ")
    movie_df["Genre"] = movie_df["Genre"].str[0]
    # explode the list into multiple rows
    movie_df = movie_df.explode("Genre")
    # group by genre and count the number of movies in each genre
    genre_df = (
        movie_df.groupby("Genre").count().sort_values(by=["Movie"], ascending=False)
    )
    fig = px.pie(genre_df, values="Movie", names=genre_df.index)
    st.plotly_chart(fig, use_container_width=True)


def pie_chart_parental_rating(movie_df: pd.DataFrame):
    parental_rating_df = (
        movie_df["Rated"].value_counts().rename_axis("Rated").reset_index(name="Count")
    )
    parental_rating_df = parental_rating_df.sort_values(by=["Count"], ascending=False)
    fig = px.pie(parental_rating_df, values="Count", names=parental_rating_df["Rated"])
    st.plotly_chart(fig, use_container_width=True)


def pie_chart_country(movie_df: pd.DataFrame):
    # get a list of all countries
    country_list = movie_df["Country"]
    # seperate countries into a list
    movie_df["Country"] = movie_df["Country"].str.split(", ")
    movie_df["Country"] = movie_df["Country"].str[0]
    # explode the list into multiple rows
    movie_df = movie_df.explode("Country")
    # group by country and count the number of movies in each country
    country_df = (
        movie_df.groupby("Country").count().sort_values(by=["Movie"], ascending=False)
    )

    # group all countries with less than 5% of the total movies into 'Others'
    total_movies = country_df["Movie"].sum()
    other_movies = 0
    for index, row in country_df.iterrows():
        if row["Movie"] / total_movies < 0.01:
            other_movies += row["Movie"]
            country_df = country_df.drop(index)
    country_df.loc["Others"] = other_movies

    fig = px.pie(country_df, values="Movie", names=country_df.index)
    st.plotly_chart(fig, use_container_width=True)


def pie_chart_language(movie_df: pd.DataFrame):
    # get a list of all languages
    language_list = movie_df["Language"]

    # seperate languages into a list, keep only the first language listed
    movie_df["Language"] = movie_df["Language"].str.split(", ")
    movie_df["Language"] = movie_df["Language"].str[0]

    # explode the list into multiple rows
    movie_df = movie_df.explode("Language")
    # group by language and count the number of movies in each language
    language_df = (
        movie_df.groupby("Language").count().sort_values(by=["Movie"], ascending=False)
    )

    # group all languages with less than 5% of the total movies into 'Others'
    total_movies = language_df["Movie"].sum()
    other_movies = 0
    for index, row in language_df.iterrows():
        if row["Movie"] / total_movies < 0.01:
            other_movies += row["Movie"]
            language_df = language_df.drop(index)
    language_df.loc["Others"] = other_movies

    fig = px.pie(language_df, values="Movie", names=language_df.index)
    st.plotly_chart(fig, use_container_width=True)

@add_seperator
def top_movies_by_genre(movie_df: pd.DataFrame, genre: str, sort_criteria: str):
    # drop NA values from Genre
    movie_df = movie_df.dropna(subset=["Genre"])
    
    # get movies where genre is in the list of genres
    genre_df = movie_df[movie_df["Genre"].str.contains(genre)]
     
    if sort_criteria == "Your Rating":
        # drop NA values
        genre_df = genre_df.dropna(subset=["Your Rating"])
        genre_df = genre_df.sort_values(by=["Your Rating", "IMDB Rating"], ascending=False)
        y=color= "Your Rating"
    
    elif sort_criteria == "IMDB Rating":
        # drop NA values
        genre_df = genre_df.dropna(subset=["IMDB Rating"])
        genre_df = genre_df.sort_values(by=["IMDB Rating", "Your Rating"], ascending=False)
        y=color= "IMDB Rating"
        
    elif sort_criteria == "Runtime":
        # drop NA values
        genre_df = genre_df.dropna(subset=["Runtime (min)"])
        genre_df = genre_df.sort_values(by=["Runtime (min)"], ascending=False)
        y=color= "Runtime (min)"
    
    elif sort_criteria == "Box Office":
        # drop NA values
        genre_df = genre_df.dropna(subset=["BoxOffice"])
        genre_df = genre_df.sort_values(by=["BoxOffice"], ascending=False)
        y=color = "BoxOffice"
    
    genre_df = genre_df.set_index("Movie")
    fig = px.bar(
        genre_df,
        x=genre_df.index,
        y=y,
        color=color,
        title=f"All {genre} Movies Ranked By {sort_criteria}",
        color_continuous_scale=px.colors.sequential.Mint,
        height=800,
    )
    st.plotly_chart(fig, use_container_width=True)
      

@add_seperator  
def top_movies_by_language(movie_df, language):
    # drop NA values from Language
    movie_df = movie_df.dropna(subset=["Language"])
    
    # get movies where language is in the list of languages
    language_df = movie_df[movie_df["Language"].str.contains(language)]
    
    # drop NA values
    language_df = language_df.dropna(subset=["Your Rating"])
    
    # sort by Your Rating and IMDB Rating
    language_df = language_df.sort_values(by=["Your Rating", "IMDB Rating"], ascending=False)
    language_df = language_df.set_index("Movie")
    fig = px.bar(
        language_df,
        x=language_df.index,
        y="Your Rating",
        color="Your Rating",
        title=f"All {language} Movies Ranked By Your Rating",
        color_continuous_scale=px.colors.sequential.ice_r,
        height=800,
    )
    st.plotly_chart(fig, use_container_width=True)
    
    
# def top_10_movies_by_language(movie_df):
#     movie_df['Language'] = movie_df['Language'].str.split(', ').str[0]
#     top_10_movies_by_language = movie_df.groupby('Language').count().sort_values(by=['Movie'], ascending=False)
#     print(f'Top 10 movies by language in {YEAR}')
#     print(tabulate(tabular_data=top_10_movies_by_language[['Movie']].head(10), headers = ['Language', 'Count'], tablefmt = 'fancy_grid', showindex=True))


# def top_10_movies_by_country(movie_df):
#     movie_df['Country'] = movie_df['Country'].str.split(', ').str[0]
#     top_10_movies_by_country = movie_df.groupby('Country').count().sort_values(by=['Movie'], ascending=False)
#     print(f'Top 10 movies by country in {YEAR}')
#     print(tabulate(tabular_data=top_10_movies_by_country[['Movie']].head(10), headers = ['Country', 'Count'], tablefmt = 'fancy_grid', showindex=True))


# def first_and_last_movie_watched(movie_df):
#     first_movie_watched = movie_df.sort_values(by=['Watched Date'], ascending=True)
#     first=first_movie_watched["Movie"].head(1).to_string(index=False)
#     first_date=first_movie_watched["Watched Date"].head(1).to_string(index=False)

#     last_movie_watched = movie_df.sort_values(by=['Watched Date'], ascending=False)
#     last=last_movie_watched["Movie"].head(1).to_string(index=False)
#     last_date=last_movie_watched["Watched Date"].head(1).to_string(index=False)

#     print(tabulate(tabular_data=[['First Movie Watched', first, first_date], ['Last Movie Watched', last, last_date]], headers = ['#', 'Movie', 'Watched Date'], tablefmt = 'fancy_grid', showindex=False))


# def top_10_box_office_flops(movie_df):
#     top_10_box_office_flops = movie_df.sort_values(by=['BoxOffice'], ascending=True)
#     # convert BoxOffice to millions and round to 2 decimal places and prefix with $ sign
#     top_10_box_office_flops['BoxOffice'] = top_10_box_office_flops['BoxOffice']
#     top_10_box_office_flops['BoxOffice'] = "$" + top_10_box_office_flops['BoxOffice'].astype(str)
#     print(f'Top 10 box office flops in {YEAR}')
#     print(tabulate(tabular_data=top_10_box_office_flops[['Movie', 'BoxOffice']].head(10), headers = 'keys', tablefmt = 'fancy_grid', showindex=False))


# def top_10_imdb_rating_flops(movie_df):
#     top_10_imdb_rating_flops = movie_df.sort_values(by=['IMDB Rating'], ascending=True)
#     print(f'Top 10 IMDB rating flops in {YEAR}')
#     print(tabulate(tabular_data=top_10_imdb_rating_flops[['Movie', 'IMDB Rating']].head(10), headers = 'keys', tablefmt = 'fancy_grid', showindex=False))


# def top_10_worst_movies_by_your_rating(movie_df):
#     top_10_worst_movies_by_your_rating = movie_df.sort_values(by=['Rating'], ascending=True)
#     print(f'Top 10 worst movies by your rating in {YEAR}')
#     print(tabulate(tabular_data=top_10_worst_movies_by_your_rating[['Movie', 'Rating']].head(10), headers = 'keys', tablefmt = 'fancy_grid', showindex=False))


# def shortest_and_longest_movie_watched(movie_df):
#     shortest_movie_watched = movie_df.sort_values(by=['Runtime (min)'], ascending=True)
#     shortest=shortest_movie_watched["Movie"].head(1).to_string(index=False)
#     shortest_runtime=shortest_movie_watched["Runtime (min)"].head(1).to_string(index=False)

#     longest_movie_watched = movie_df.sort_values(by=['Runtime (min)'], ascending=False)
#     longest=longest_movie_watched["Movie"].head(1).to_string(index=False)
#     longest_runtime=longest_movie_watched["Runtime (min)"].head(1).to_string(index=False)
#     print(tabulate(tabular_data=[['Shortest Movie Watched', shortest, shortest_runtime], ['Longest Movie Watched', longest, longest_runtime]], headers = ['#', 'Movie', 'Runtime (min)'], tablefmt = 'fancy_grid', showindex=False))


# def total_time_watched(movie_df):
#     total_minutes_watched = movie_df['Runtime (min)'].sum()
#     # convert minutes to hours and minutes
#     hours, minutes = divmod(total_minutes_watched, 60)
#     hours, minutes = int(hours), int(minutes)
#     print(tabulate(tabular_data=[['Total Hours Watched', f'{hours} hours and {minutes} minutes']], headers = ['#', 'Runtime Sum'], tablefmt = 'fancy_grid', showindex=False))


# def average_movie_rating(movie_df):
#     average_movie_rating = movie_df['Rating'].mean().round(2)
#     print(tabulate(tabular_data=[['Average Movie Rating', average_movie_rating]], headers = ['#', 'Rating'], tablefmt = 'fancy_grid', showindex=False))


# def average_movie_runtime(movie_df):
#     average_movie_runtime = movie_df['Runtime (min)'].mean()
#     # convert minutes to hours and minutes
#     hours, minutes = divmod(average_movie_runtime, 60)
#     hours, minutes = int(hours), int(minutes)
#     print(tabulate(tabular_data=[['Average Movie Runtime', f'{hours} hours and {minutes} minutes']], headers = ['#', 'Runtime (min)'], tablefmt = 'fancy_grid', showindex=False))


# def oldest_release_date(movie_df):
#     oldest_release_date = movie_df.sort_values(by=['Year'], ascending=True)
#     oldest=oldest_release_date["Movie"].head(1).to_string(index=False)
#     oldest_release=oldest_release_date["Year"].head(1).to_string(index=False)
#     print(tabulate(tabular_data=[['Oldest Release Date', oldest, oldest_release]], headers = ['#', 'Movie', 'Release Date'], tablefmt = 'fancy_grid', showindex=False))


# def adult_movies_watched(movie_df):
#     adult_movies_watched = movie_df[movie_df['Rated'] == 'R']
#     print(f'Adult movies watched in {YEAR}: {adult_movies_watched["Movie"].count()}')
#     print(tabulate(tabular_data=adult_movies_watched[['Movie', 'Rated']], headers = 'keys', tablefmt = 'fancy_grid', showindex=False))


# def highly_rated_but_imdb_low(movie_df:pd.DataFrame):
#     # check the imdb score for highly rated movies (8.0+) but low Rating (4.0-)
#     highly_rated_but_imdb_low = movie_df[(movie_df['IMDB Rating'] >= 8.0) & (movie_df['Rating'] <= 4.0)]
#     print(f'Highly rated by audiences but low Rating by you in {YEAR}: {highly_rated_but_imdb_low["Movie"].count()}')
#     print(tabulate(tabular_data=highly_rated_but_imdb_low[['Movie', 'IMDB Rating', 'Rating']], headers = 'keys', tablefmt = 'fancy_grid', showindex=False))


# def lowly_rated_but_imdb_high(movie_df):
#     # check the imdb score for lowly rated movies (4.0-) but highly rated (8.0+) by you
#     lowly_rated_but_imdb_high = movie_df[(movie_df['IMDB Rating'] <= 4.0) & (movie_df['Rating'] >= 8.0)]
#     print(f'Lowly rated by audiences but highly rated by you in {YEAR}: {lowly_rated_but_imdb_high["Movie"].count()}')
#     print(tabulate(tabular_data=lowly_rated_but_imdb_high[['Movie', 'IMDB Rating', 'Rating']], headers = 'keys', tablefmt = 'fancy_grid', showindex=False))


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


# #########################
# FRONT-END SECTION START #
# #########################

# PAGE CONFIG
st.set_page_config(
    page_title="Letterboxd Analysis",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# PAGE TITLE
st.title(":orange[Letterboxd] Movie Analysis :popcorn:")

st.warning(
    "Please Note: This part of the app is still under construction. Check back soon for updates! 🚧"
)

# INTRO
st.markdown(
    """   

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
st.warning(
    "Please Note: CSV should not contain more than 1000 movies. OMDB API has a limit of 1000 requests per day. If you have more than 1000 movies, please split your CSV into multiple CSVs and upload them separately using different OMDB API Keys. 🛑"
)

col1, col2 = st.columns(2, gap="large")
with col1:
    st.info(
        "Don't have a Letterboxd account? Create one [here](https://www.letterboxd.com/)."
    )

with col2:
    st.info("Don't have a Letterboxd export file? Get an example one below 👇🏻")

    col1, col2, col3 = st.columns([3, 3, 1], gap="small")
    with col1:
        with open("pages/sample-csv/letterboxd_diary.csv", "rb") as letterboxd_diary:
            btn = st.download_button(
                label="Download Diary Export Example",
                data=letterboxd_diary,
                file_name="letterboxd_diary.csv",
                mime="text/csv",
                help="This is an example Letterboxd export file. You can use this to test out the app.",
            )

    with col2:
        with open(
            "pages/sample-csv/letterboxd_ratings.csv", "rb"
        ) as letterboxd_ratings:
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

user_api_key = st.text_input(
    "Enter your OMBD API key here",
    placeholder="Eight lettered OMDB API key",
    help="You can get your OMDB API key from here: http://www.omdbapi.com/apikey.aspx",
)


# TODO: ADD A INPUT BOX FOR USERS TO ENTER THEIR OMBD KEY HERE AND MAKE ONE REQUEST TO CHECK ITS AUTHENTICITY. PROGRESS ONLY IF KEY IS VALID. MENTION THAT WE DO NOT STORE THE KEY IN ANY WAY. REQUEST LIMIT PER DAY IS 1000. PASS THAT KEY TI get_extend_dataframe_from_api function instead of using your own key.

if diary_file is not None:
    # VERIFY FILE -> DIARY
    diary_df = pd.read_csv(diary_file, encoding="utf-8", header=0)
    cols_to_check = ["Date", "Name", "Year", "Letterboxd URI", "Rating", "Watched Date"]
    if set(cols_to_check).issubset(set(diary_df.columns)):
        st.success("Diary file uploaded successfully!")
        diary_df = diary_df[cols_to_check]

    else:
        st.error(
            "Diary file is not valid. Please upload a valid Letterboxd diary export file."
        )
        st.stop()

if ratings_file is not None:
    # VERIFY FILE -> RATINGS
    ratings_df = pd.read_csv(ratings_file, encoding="utf-8", header=0)
    cols_to_check = ["Date", "Name", "Year", "Rating"]
    if set(cols_to_check).issubset(set(ratings_df.columns)):
        st.success("Ratings file uploaded successfully!")
        ratings_df = ratings_df[cols_to_check]

    else:
        st.error(
            "Ratings file is not valid. Please upload a valid Letterboxd ratings export file."
        )
        st.stop()


if len(user_api_key) == 8:
    KEY_VERIFICATION_PASSED = False
    # get the movie name and year from the first row of the dataframe
    name = "Reservoir Dogs"
    year = 1992
    base_url = "http://www.omdbapi.com/?"
    parameters = {"apikey": user_api_key, "t": name, "y": year}
    params_encoded = urllib.parse.urlencode(
        parameters, quote_via=urllib.parse.quote, safe=""
    )
    url = base_url + params_encoded

    response = requests.get(url).json()

    # check status code of the response
    if response["Response"] == "True":
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

    # check if ratings_df['Movie'] is in diary_df['Movie'] and value matches and if so then add diary_df['Watched Date'] to movie_df['Watched Date']
    for index, row in movie_df.iterrows():
        if row["Name"] in diary_df["Name"].values:
            movie_df.loc[index, "Watched Date"] = diary_df.loc[
                diary_df["Name"] == row["Name"], "Watched Date"
            ].values[0]

    # drop the Date column from movie_df
    movie_df = movie_df.drop(columns=["Date"])

    # # check if csvs/Letterboxd folder exists and file CHECKPOINT1.csv exists, if not then run cleanup_dataframe
    if not os.path.exists("csvs/letterboxd/CHECKPOINT1.csv"):
        get_extend_dataframe_from_api(movie_df, user_api_key)

    if not os.path.exists("csvs/letterboxd/CHECKPOINT2.csv"):
        cleanup_dataframe(movie_df)

    movie_df = pd.read_csv(
        "csvs/letterboxd/CHECKPOINT2.csv", encoding="utf-8", header=0
    )

    # st.header("Data Preview")
    # st.dataframe(movie_df)
    st.markdown("---")

    total_movies_watched(movie_df)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        best_movies_by_rating(movie_df)

    with col2:
        worst_movies_by_rating(movie_df)

    st.markdown("---")
    col1, col2 = st.columns(2, gap="large")

    with col1:
        longest_movies_by_runtime(movie_df)

    with col2:
        shortest_movies_by_runtime(movie_df)

    st.markdown("---")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        best_movies_by_imdb_rating(movie_df)

    with col2:
        worst_movies_by_imdb_rating(movie_df)

    st.markdown("---")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        most_popular_movies(movie_df)

    with col2:
        most_watched_directors(movie_df)

    st.markdown("---")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        highest_grossing_movies(movie_df)

    with col2:
        lowest_grossing_movies(movie_df)


    st.info("🔖 Note: The Box Office figures are for US and Canada only, not worldwide.")


    
    st.markdown("---")
    st.header("Directory Rankings by Your Rating")

    # get a list of all directors where the number of movies they have directed is greater than 2
    st.info("🔖 Note: Only directors with more than 2 movies are shown.")
    directors = movie_df["Director"].value_counts()
    directors = directors[directors > 2]
    directors = directors.index.tolist()
    # alphabetically sort the list
    directors.sort()
    # add a None option to the list on top
    directors.insert(0, None)
    selected_director = st.selectbox(
        options=directors, label="Select Director", key="director_ranking", index=0
    )
    if selected_director is not None:
        director_films_rating_ranked(movie_df, selected_director)
    else:
        st.error("Please select a director to continue.")
        
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.header("Genre Distribution")
        pie_chart_genre(movie_df)
    with col2:
        st.header("Parental Rating Distribution")
        pie_chart_parental_rating(movie_df)

    st.info(
        "🔖 Note: These pie charts are interactive. Hover over the slices to see the exact values. Click on the legend to hide/show the slices."
    )
    
    st.markdown("---")
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.header("Country Distribution")
        pie_chart_country(movie_df)
    with col2:
        st.header("Language Distribution")
        pie_chart_language(movie_df)

    st.info(
        "🔖 Note: These pie charts are interactive. Hover over the slices to see the exact values. Click on the legend to hide/show the slices."
    )
    st.markdown("---")

    st.header("Movie Rankings by Genre")
    genre_list = movie_df["Genre"].unique().tolist()
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        # remove nan values from the list
        genre_list = [x for x in genre_list if str(x) != 'nan']
        # add None to the list on top
        genre_list.insert(0, None)
        
        
        selected_genre=st.selectbox("Select Genre", options=genre_list, key="genre_ranking", index=0)
    
    with col2:
         sorted_by=st.selectbox("Sort By", options=["Your Rating", "IMDB Rating", "Runtime", "Box Office"], key="genre_ranking_sort", index=0)
    
    st.info("Hey, if you see too many bars, select an area of the chart by draggin your mouse and zoom in. You can also zoom out by double clicking on the chart.")
    
    if selected_genre:
        top_movies_by_genre(movie_df, selected_genre, sorted_by)
    
    
    
    st.header("Movie Rankings by Language")

    lang_list = movie_df["Language"].unique().tolist()
    
    # remove nan values from the list
    lang_list = [x for x in lang_list if str(x) != 'nan']
    
    # remove '' values from the list
    lang_list = [x for x in lang_list if str(x) != '']
    
    # remove languages for which there are less than 5 movies
    lang_list = [x for x in lang_list if len(movie_df[movie_df['Language'] == x]) > 5]
     
    # add None to the list on top
    lang_list.insert(0, None)
    selected_language=st.selectbox("Select Language", options=lang_list, key="language_ranking", index=0)
    
    st.info("Hey, if you see too many bars, select an area of the chart by draggin your mouse and zoom in. You can also zoom out by double clicking on the chart.")
        
    if selected_language:
        top_movies_by_language(movie_df, selected_language)
    
     