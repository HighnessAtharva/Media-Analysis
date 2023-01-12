import urllib
import requests
import pandas as pd
import json
import os
from tabulate import tabulate


#######################
# DATA CLEANUP START #
#######################

def cleanup_dataframe(games_df: pd.DataFrame):    
    
    # drop id column
    games_df = games_df.drop('id', axis=1)
    
    # keep only year part of release_date
    games_df['release_date'] = pd.to_datetime(games_df['release_date'])
    games_df['release_date'] = games_df['release_date'].dt.year

    # rename release_dated to released
    games_df = games_df.rename(columns={'release_date': 'released'})

    # create empty column genres
    games_df['genres'] = pd.Series(dtype=object)  

    # create empty platform columns
    games_df['platforms'] = pd.Series(dtype=object)

    # shift the second last column to first position
    games_df.insert(0, 'genres', games_df.pop('genres'))
    games_df.insert(1, 'Year', games_df.pop('Year'))  

    # rename Year column to last_played
    games_df = games_df.rename(columns={'Year': 'last_played'})

    #############
    # GENRES
    #############

    # genre columns are columns 15-end
    genre_columns =  games_df.columns[14:]

    # iterrate over each row
    for index, row in games_df.iterrows():
        to_add = [column for column in genre_columns if row[column] == 'x']
        games_df.at[index, 'genres'] = ', '.join(to_add)

    # drop the genre_columns
    games_df = games_df.drop(genre_columns, axis=1)


    #############
    # PLATFORMS
    #############

    # platforms columns are mac, linux, windows, steamdeck
    my_platforms = ['mac', 'linux', 'win', 'steam deck']

    for index, row in games_df.iterrows():
        to_add = [column for column in my_platforms if row[column] == 'x']
        if not to_add:
            to_add.append('-')
        games_df.at[index, 'platforms'] = ', '.join(to_add)
  
    
    
    # drop the platform columns
    games_df = games_df.drop(my_platforms, axis=1)

    # move game column to first place
    games_df.insert(0, 'game', games_df.pop('game'))

    # drop other unnecessary columns
    games_df = games_df.drop('wilsonscore', axis=1)
    games_df = games_df.drop('sdbrating', axis=1)

    
    # fill 0 where hours is NA
    games_df['hours'] = games_df['hours'].fillna(0)
    
    # fill "NA" where metascore is NA
    games_df['metascore'] = games_df['metascore'].fillna('-')
    
    # # fill "NA" where Userscore is NA
    games_df['userscore'] = games_df['userscore'].fillna('-')
    
    # fill "NA" where platforms is NA
    games_df['platforms'] = games_df['platforms'].fillna('-')
    
    print(games_df)
    # print(games_df.loc[1])
    # print(games_df.loc[2])
    games_df.to_csv('CHECKPOINT1.csv', index=False, encoding='utf-8')

    
#######################
# DATA ANALYSIS START #
#######################

def pretty_printer():
    print("""
          ----------------8<-------------[ Annual Videogame Report ]------------------
          """)
    

YEAR = 2022
games_df = pd.read_csv('steam-library.csv', encoding='utf-8', header=0)

# get rid of rows where 'last_played' column does not contain '2022'
games_df['last_played']=pd.to_datetime(games_df['last_played'])
games_df['Year'] = games_df['last_played'].dt.year
games_df = games_df[games_df['Year'] == YEAR]

# remove last_played column
games_df = games_df.drop('last_played', axis=1)


# LOAD/PROCESS CHECKPOINT 1  
if os.path.isfile('CHECKPOINT1.csv'):
    games_df = pd.read_csv('CHECKPOINT1.csv', encoding='utf-8')
    print(f'Loaded checkpoint file #1. Continuing from {len(games_df)} games.')
else:
    cleanup_dataframe(games_df)

