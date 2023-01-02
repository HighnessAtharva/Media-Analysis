import urllib
import requests
import pandas as pd
import json
import os
from tabulate import tabulate

#######################
# DATA CLEANUP START #
#######################

def get_omdb_data(title, release_year):
    # # get the API key from the environment variables
     
    API_KEY = os.environ.get('OMDB_API_KEY')
    base_url = 'http://www.omdbapi.com/?'
    parameters = {'apikey': API_KEY, 't': title, 'y': release_year}
    params_encoded = urllib.parse.urlencode(
        parameters, quote_via=urllib.parse.quote, safe='')
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

def get_extend_dataframe_from_api(movie_df: pd.DataFrame):
    skipped_movies = []
    for idx, movie in enumerate(movie_df.iterrows(), start=1):
        try:
            # get omdb data for it and add it to the dataframe
            name = movie[1]['Name']
            year = int(movie[1]['Year'])
            omdb_data = get_omdb_data(name, year)

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

            # print progress status
            print(f'{idx}. ✅ Added data for {name} ({year})')

        except Exception as e:
            name = movie[1]['Name']
            print(f'{idx}. ❌ Skipping {name} due to error: {e.__class__}')
            skipped_movies.append(name)
            
    # SAVE CHECKPOINT
    print(f"Total movies skipped: {len(skipped_movies)}")
    print(skipped_movies)
    print(f"Processed {len(movie_df)-len(skipped_movies)}. Writing to CSV file. Saving Checkpoint!")
    movie_df.to_csv('CHECKPOINT1.csv', index=False, encoding='utf-8')


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
    
    # SAVE CHECKPOINT
    movie_df.to_csv('CHECKPOINT2.csv', index=False, encoding='utf-8') 

    
    
#######################
# DATA ANALYSIS START #
#######################

def pretty_printer():
    print("""
          ----------------8<-------------[ Annual Movie Report ]------------------
          """)
    
    
def total_movies_watched(movie_df: pd.DataFrame):
    total_movies_watched = len(movie_df)
    print(tabulate([['Total movies watched', total_movies_watched]], headers=['Metric', 'Value'], tablefmt='fancy_grid'))
    pretty_printer()

def top_10_movies_by_rating(movie_df: pd.DataFrame):
    top_10_movies_by_rating = movie_df.sort_values(by=['Rating'], ascending=False)
    print(f'Top 10 movies in {YEAR}')
    print(tabulate(tabular_data=top_10_movies_by_rating[['Name', 'Rating']].head(10).values, headers=['Movie', 'Your Rating'], tablefmt='fancy_grid'))
    pretty_printer()
    
def top_10_movies_by_runtime(movie_df):
    top_10_movies_by_runtime = movie_df.sort_values(by=['Runtime'], ascending=False)
    print(f'Top 10 movies by runtime in {YEAR}')
    print(tabulate(tabular_data=top_10_movies_by_runtime[['Name', 'Runtime']].head(10).values, headers=['Movie', 'Runtime (mins)'], tablefmt='fancy_grid'))
    pretty_printer()
    
def top_10_movies_by_imdb_rating(movie_df):
    top_10_movies_by_imdb_rating = movie_df.sort_values(by=['imdbRating'], ascending=False)
    print(f'Top 10 movies by IMDB rating in {YEAR}')
    print(tabulate(tabular_data=top_10_movies_by_imdb_rating[['Name', 'imdbRating']].head(10).values, headers=['Movie', 'IMDB Rating'], tablefmt='fancy_grid'))
    pretty_printer()
 
def top_10_movies_by_imdb_votes(movie_df):
    # remove commas from imdbVotes column
    movie_df['imdbVotes'] = movie_df['imdbVotes'].str.replace(',', '')
    
    # convert imdbVotes to numeric
    movie_df['imdbVotes'] = pd.to_numeric(movie_df['imdbVotes'], errors='coerce')
    
    # divide imdbVotes by 1000 to get the number of thousands of votes
    movie_df['imdbVotes'] = (movie_df['imdbVotes'] / 1000).round(0)
    
    
    top_10_movies_by_imdb_votes = movie_df.sort_values(by=['imdbVotes'], ascending=False)
    
    # append 'K' to the end of the imdbVotes column
    top_10_movies_by_imdb_votes['imdbVotes'] = top_10_movies_by_imdb_votes['imdbVotes'].astype(str) + ' K'
    
    # remove .0 from the end of the imdbVotes column
    top_10_movies_by_imdb_votes['imdbVotes'] = top_10_movies_by_imdb_votes['imdbVotes'].str.replace('.0 K', ' K')
    
    
    print(f'Top 10 movies by IMDB votes in {YEAR}')
    print(tabulate(tabular_data=top_10_movies_by_imdb_votes[['Name', 'imdbVotes']].head(10).values, headers=['Movie', 'IMDB Votes'], tablefmt='fancy_grid'))
    pretty_printer()
 
def top_10_movies_by_box_office(movie_df):
    top_10_movies_by_box_office = movie_df.sort_values(by=['BoxOffice'], ascending=False)
    # convert BoxOffice to millions and round to 2 decimal places and prefix with $ sign
    top_10_movies_by_box_office['BoxOffice'] = (top_10_movies_by_box_office['BoxOffice'] / 1000000).round(2)
    top_10_movies_by_box_office['BoxOffice'] = "$" + top_10_movies_by_box_office['BoxOffice'].astype(str) + ' M'
    print(f'Top 10 movies by box office in {YEAR}')
    print(tabulate(top_10_movies_by_box_office[['Name', 'BoxOffice']].head(10), headers = 'keys', tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()
    
 
 
def top_10_movies_by_genre(movie_df):
    # seperate genres into a list
    movie_df['Genre'] = movie_df['Genre'].str.split(', ')
    # explode the list into multiple rows
    movie_df = movie_df.explode('Genre')
    # group by genre and count the number of movies in each genre
    top_10_movies_by_genre = movie_df.groupby('Genre').count().sort_values(by=['Name'], ascending=False)
    print(f'Top 10 movies by genre in {YEAR}')
    print(tabulate(tabular_data=top_10_movies_by_genre[['Name']].head(10), headers = ['Genre', 'Count'], tablefmt = 'fancy_grid', showindex=True))
    pretty_printer()

 
def top_10_movies_by_director(movie_df):
    top_10_movies_by_director = movie_df.groupby('Director').count().sort_values(by=['Name'], ascending=False)
    print(f'Top 10 movies by director in {YEAR}')
    print(tabulate(tabular_data=top_10_movies_by_director[['Name']].head(10), headers = ['Director', 'Count'], tablefmt = 'fancy_grid', showindex=True))
    pretty_printer()
    
def top_10_movies_by_language(movie_df):
    movie_df['Language'] = movie_df['Language'].str.split(', ').str[0]
    top_10_movies_by_language = movie_df.groupby('Language').count().sort_values(by=['Name'], ascending=False)
    print(f'Top 10 movies by language in {YEAR}')
    print(tabulate(tabular_data=top_10_movies_by_language[['Name']].head(10), headers = ['Language', 'Count'], tablefmt = 'fancy_grid', showindex=True))
    pretty_printer()
 
def top_10_movies_by_country(movie_df):
    movie_df['Country'] = movie_df['Country'].str.split(', ').str[0]
    top_10_movies_by_country = movie_df.groupby('Country').count().sort_values(by=['Name'], ascending=False)
    print(f'Top 10 movies by country in {YEAR}')
    print(tabulate(tabular_data=top_10_movies_by_country[['Name']].head(10), headers = ['Country', 'Count'], tablefmt = 'fancy_grid', showindex=True))
    pretty_printer()
    
    
def first_and_last_movie_watched(movie_df):
    first_movie_watched = movie_df.sort_values(by=['Watched Date'], ascending=True)
    first=first_movie_watched["Name"].head(1).to_string(index=False)
    first_date=first_movie_watched["Watched Date"].head(1).to_string(index=False)
    
    last_movie_watched = movie_df.sort_values(by=['Watched Date'], ascending=False)
    last=last_movie_watched["Name"].head(1).to_string(index=False)
    last_date=last_movie_watched["Watched Date"].head(1).to_string(index=False)
     
    print(tabulate(tabular_data=[['First Movie Watched', first, first_date], ['Last Movie Watched', last, last_date]], headers = ['#', 'Movie', 'Watched Date'], tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()

def top_10_box_office_flops(movie_df):
    top_10_box_office_flops = movie_df.sort_values(by=['BoxOffice'], ascending=True)
    # convert BoxOffice to millions and round to 2 decimal places and prefix with $ sign
    top_10_box_office_flops['BoxOffice'] = top_10_box_office_flops['BoxOffice'] 
    top_10_box_office_flops['BoxOffice'] = "$" + top_10_box_office_flops['BoxOffice'].astype(str)
    print(f'Top 10 box office flops in {YEAR}')
    print(tabulate(tabular_data=top_10_box_office_flops[['Name', 'BoxOffice']].head(10), headers = 'keys', tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()
    
def top_10_imdb_rating_flops(movie_df):
    top_10_imdb_rating_flops = movie_df.sort_values(by=['imdbRating'], ascending=True)
    print(f'Top 10 IMDB rating flops in {YEAR}')
    print(tabulate(tabular_data=top_10_imdb_rating_flops[['Name', 'imdbRating']].head(10), headers = 'keys', tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()
    
def top_10_worst_movies_by_your_rating(movie_df):
    top_10_worst_movies_by_your_rating = movie_df.sort_values(by=['Rating'], ascending=True)
    print(f'Top 10 worst movies by your rating in {YEAR}')
    print(tabulate(tabular_data=top_10_worst_movies_by_your_rating[['Name', 'Rating']].head(10), headers = 'keys', tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()

def shortest_and_longest_movie_watched(movie_df):
    shortest_movie_watched = movie_df.sort_values(by=['Runtime'], ascending=True)
    shortest=shortest_movie_watched["Name"].head(1).to_string(index=False)
    shortest_runtime=shortest_movie_watched["Runtime"].head(1).to_string(index=False)
    
    longest_movie_watched = movie_df.sort_values(by=['Runtime'], ascending=False)
    longest=longest_movie_watched["Name"].head(1).to_string(index=False)
    longest_runtime=longest_movie_watched["Runtime"].head(1).to_string(index=False)
    print(tabulate(tabular_data=[['Shortest Movie Watched', shortest, shortest_runtime], ['Longest Movie Watched', longest, longest_runtime]], headers = ['#', 'Movie', 'Runtime'], tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()
    
def total_time_watched(movie_df):
    total_minutes_watched = movie_df['Runtime'].sum()
    # convert minutes to hours and minutes
    hours, minutes = divmod(total_minutes_watched, 60)
    hours, minutes = int(hours), int(minutes)
    print(tabulate(tabular_data=[['Total Hours Watched', f'{hours} hours and {minutes} minutes']], headers = ['#', 'Runtime Sum'], tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()
    
def average_movie_rating(movie_df):
    average_movie_rating = movie_df['Rating'].mean().round(2)
    print(tabulate(tabular_data=[['Average Movie Rating', average_movie_rating]], headers = ['#', 'Rating'], tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()
    
def average_movie_runtime(movie_df):
    average_movie_runtime = movie_df['Runtime'].mean()
    # convert minutes to hours and minutes
    hours, minutes = divmod(average_movie_runtime, 60)
    hours, minutes = int(hours), int(minutes)
    print(tabulate(tabular_data=[['Average Movie Runtime', f'{hours} hours and {minutes} minutes']], headers = ['#', 'Runtime'], tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()

def oldest_release_date(movie_df):
    oldest_release_date = movie_df.sort_values(by=['Year'], ascending=True)
    oldest=oldest_release_date["Name"].head(1).to_string(index=False)
    oldest_release=oldest_release_date["Year"].head(1).to_string(index=False)
    print(tabulate(tabular_data=[['Oldest Release Date', oldest, oldest_release]], headers = ['#', 'Movie', 'Release Date'], tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()

def adult_movies_watched(movie_df):
    adult_movies_watched = movie_df[movie_df['Rated'] == 'R']
    print(f'Adult movies watched in {YEAR}: {adult_movies_watched["Name"].count()}')
    print(tabulate(tabular_data=adult_movies_watched[['Name', 'Rated']], headers = 'keys', tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()
    
def highly_rated_but_imdb_low(movie_df):
    # check the imdb score for highly rated movies (8.0+) but low Rating (4.0-)
    highly_rated_but_imdb_low = movie_df[(movie_df['imdbRating'] >= 8.0) & (movie_df['Rating'] <= 4.0)]
    print(f'Highly rated by audiences but low Rating by you in {YEAR}: {highly_rated_but_imdb_low["Name"].count()}')
    print(tabulate(tabular_data=highly_rated_but_imdb_low[['Name', 'imdbRating', 'Rating']], headers = 'keys', tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()
     
     
def lowly_rated_but_imdb_high(movie_df):
    # check the imdb score for lowly rated movies (4.0-) but highly rated (8.0+) by you
    lowly_rated_but_imdb_high = movie_df[(movie_df['imdbRating'] <= 4.0) & (movie_df['Rating'] >= 8.0)]
    print(f'Lowly rated by audiences but highly rated by you in {YEAR}: {lowly_rated_but_imdb_high["Name"].count()}')
    print(tabulate(tabular_data=lowly_rated_but_imdb_high[['Name', 'imdbRating', 'Rating']], headers = 'keys', tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()

# TODO: Function needs to be tested
def longest_watch_streak(movie_df):
    from datetime import timedelta
    # sort by date
    movie_df = movie_df.sort_values(by=['Watched Date'], ascending=True)
    # create a new column with the difference between the current date and the previous date
    movie_df['Watched Date'] = pd.to_datetime(movie_df['Watched Date'])
    movie_df['streak'] = movie_df['Watched Date'].diff()

    # select date column where streak is max
    longest_streak = movie_df.loc[movie_df['streak'].idxmax()]
    jump_days = longest_streak['streak'].days+1
    
    # go back jump_day rows to get the movie before the longest streak
    movie_before_streak = movie_df.iloc[movie_df.index.get_loc(longest_streak.name) - jump_days]
    
    # get the date of the movie before the longest streak
    start = movie_before_streak['Watched Date'].date()
     
    # add the jump_days to the start date to get the end date
    end = start + timedelta(days=jump_days)
    end = end.strftime('%Y-%m-%d')    
    print(tabulate(tabular_data=[['Longest Watch Streak', f'{jump_days} days', start, end]], headers = ['#', 'Days', 'Start', 'End'], tablefmt = 'fancy_grid', showindex=False))
    pretty_printer()

def most_watched_month(movie_df):
    pass

def least_watched_month(movie_df):
    pass



YEAR = 2022
movies = pd.read_csv('diary.csv', encoding='utf-8',
                     header=0, usecols=['Name', 'Year', 'Watched Date', 'Rating'])
# filter movies by year 
movie_df = movies[movies['Watched Date'].str.contains(str(YEAR))]


# LOAD/PROCESS CHECKPOINT 1  
if os.path.isfile('CHECKPOINT1.csv'):
    movie_df = pd.read_csv('CHECKPOINT1.csv', encoding='utf-8')
    print(f'Loaded checkpoint file #1. Continuing from {len(movie_df)} movies.')
else:
    get_extend_dataframe_from_api(movie_df)

# LOAD/PROCESS CHECKPOINT 2   
if os.path.isfile('CHECKPOINT2.csv'):
    movie_df = pd.read_csv('CHECKPOINT2.csv', encoding='utf-8')
    print(f'Loaded checkpoint file #2. Continuing from {len(movie_df)} movies.')
else:
    cleanup_dataframe(movie_df)
    

total_movies_watched(movie_df)
total_time_watched(movie_df)
average_movie_rating(movie_df)
adult_movies_watched(movie_df)
average_movie_runtime(movie_df)
longest_watch_streak(movie_df)
top_10_movies_by_rating(movie_df)
top_10_movies_by_runtime(movie_df)
top_10_movies_by_imdb_rating(movie_df)
top_10_movies_by_imdb_votes(movie_df)
top_10_movies_by_box_office(movie_df)
top_10_movies_by_genre(movie_df)
top_10_movies_by_director(movie_df)
top_10_movies_by_language(movie_df)
top_10_movies_by_country(movie_df)
first_and_last_movie_watched(movie_df)
top_10_box_office_flops(movie_df)
top_10_imdb_rating_flops(movie_df)
top_10_worst_movies_by_your_rating(movie_df)
shortest_and_longest_movie_watched(movie_df)
oldest_release_date(movie_df)
highly_rated_but_imdb_low(movie_df)
lowly_rated_but_imdb_high(movie_df)




