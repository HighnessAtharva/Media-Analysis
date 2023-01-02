import urllib
import requests
import pandas as pd
import json
import os
from tabulate import tabulate


#######################
# DATA CLEANUP START #
#######################
def cleanup_dataframe(books_df: pd.DataFrame):
    # check for null values and drop them
    books_df = books_df.dropna(how='all', axis=0)

    # split the title on the first occurence of ( and take the first part
    books_df['Title'] = books_df['Title'].str.split('(', n=1, expand=True)[0]

    # drop the year column since we don't need it anymore
    books_df = books_df.drop(['Year'], axis=1)

    # filter out rows where exclusive shelf value == read
    books_df = books_df[books_df['Exclusive Shelf'] == 'read']

    # strip whitespaces from all rows
    books_df = books_df.apply(lambda x: x.str.strip()
                              if x.dtype == "object" else x)

    # write the dataframe to a csv file
    books_df.to_csv('CHECKPOINT1.csv', index=False, encoding='utf-8')

#######################
# DATA ANALYSIS START #
#######################


def pretty_printer():
    print("""
          ----------------8<-------------[ Annual Book Report ]------------------
          """)


def total_books_read(books_df: pd.DataFrame):
    print(f"Total Books Read in {YEAR}")
    print(tabulate(tabular_data=[[len(books_df)]], headers=['Total Books Read'],
          tablefmt='fancy_grid'))
    pretty_printer()


def top_N_authors(books_df: pd.DataFrame, N: int = 10):
    print(f"Top {N} Authors in {YEAR}")
    # count the number of books read by each author should be greater than 1
    author_count = books_df['Author'].value_counts()
    author_count = author_count[author_count > 1]
    if N > len(author_count):
        print(
            f"WARNING: N is greater than the number of authors in the dataframe. Setting N to {len(author_count)}")
    print(tabulate(tabular_data=author_count.head(N).to_frame(),
          headers=['Author', 'Books Read'], tablefmt='fancy_grid'))
    pretty_printer()


def top_N_rated_books(books_df: pd.DataFrame, N: int = 10):
    books_df = books_df[books_df['My Rating'] > 0]
    # store only the columns we are interested in
    books_df = books_df[['Title', 'Author', 'My Rating', 'Average Rating']]

    print(
        f"Top {N} Rated Books in {YEAR} (Sorted by My Rating first and then by Average Rating)")
    # sort the dataframe by My Rating and Average Rating
    books_df = books_df.sort_values(
        by=['My Rating', 'Average Rating'], ascending=False)

    print(tabulate(tabular_data=books_df.head(N), headers='keys',
          tablefmt='fancy_grid'))
    pretty_printer()


def top_N_publishers(books_df: pd.DataFrame, N: int = 10):
    print(f"Top {N} Publishers in {YEAR}")
    # count the number of books read by each author should be greater than 1
    publisher_count = books_df['Publisher'].value_counts()
    publisher_count = publisher_count[publisher_count > 1]
    if N > len(publisher_count):
        print(
            f"WARNING: N is greater than the number of publishers in the dataframe. Setting N to {len(publisher_count)}")
    print(tabulate(tabular_data=publisher_count.head(N).to_frame(),
          headers=['Publisher', 'Books Read'], tablefmt='fancy_grid'))
    pretty_printer()


def average_rating(books_df: pd.DataFrame):
    print(f"Average Rating of Books Read in {YEAR}")
    # count the number of books read by each author should be greater than 1
    avg_rating = books_df['My Rating'].mean()
    print(tabulate(tabular_data=[[avg_rating]], headers=[
          'Average Rating'], tablefmt='fancy_grid'))
    pretty_printer()


def top_N_binding(books_df: pd.DataFrame, N: int = 10):
    print(f"Top {N} Binding Types in {YEAR}")
    # count the number of books read by each author should be greater than 1
    binding_count = books_df['Binding'].value_counts()
    binding_count = binding_count[binding_count > 1]
    if N > len(binding_count):
        print(
            f"WARNING: N is greater than the number of bindings in the dataframe. Setting N to {len(binding_count)}")
    print(tabulate(tabular_data=binding_count.head(N).to_frame(),
          headers=['Binding', 'Books Read'], tablefmt='fancy_grid'))
    pretty_printer()


def total_pages_read(books_df: pd.DataFrame):
    print(f"Total Pages Read in {YEAR}")
    # count the number of books read by each author should be greater than 1
    total_pages = books_df['Number of Pages'].sum()
    print(tabulate(tabular_data=[[total_pages]], headers=[
          'Total Pages'], tablefmt='fancy_grid'))
    pretty_printer()


def average_pages_read(books_df: pd.DataFrame):
    print(f"Average Pages Read in {YEAR}")
    # count the number of books read by each author should be greater than 1
    avg_pages = books_df['Number of Pages'].mean()
    print(tabulate(tabular_data=[[avg_pages]], headers=[
          'Average Pages'], tablefmt='fancy_grid'))
    pretty_printer()


def shortest_and_longest_books(books_df: pd.DataFrame):
    # store only the columns we are interested in
    books_df = books_df[['Title', 'Author', 'Number of Pages']]

    print(f"Shortest and Longest Books Read in {YEAR}")
    # sort the dataframe by My Rating and Average Rating
    books_df = books_df.sort_values(
        by=['Number of Pages'], ascending=True, ignore_index=True)

    smallest = books_df.loc[0]
    largest = books_df.loc[len(books_df)-1]

    print(tabulate(tabular_data=[smallest, largest],
          headers='keys', tablefmt='fancy_grid'))
    pretty_printer()


def oldest_book_read(books_df: pd.DataFrame):
    # store only the columns we are interested in
    books_df = books_df[['Title', 'Author', 'Original Publication Year']]

    print(f"Oldest Book Read in {YEAR}")
    # sort the dataframe by My Rating and Average Rating
    books_df = books_df.sort_values(
        by=['Original Publication Year'], ascending=True, ignore_index=True)

    oldest = books_df.loc[0]

    print(tabulate(tabular_data=[oldest],
          headers='keys', tablefmt='fancy_grid'))
    pretty_printer()


def first_and_last_books_read(books_df: pd.DataFrame):
    # store only the columns we are interested in
    books_df = books_df[['Title', 'Author', 'Date Read']]

    print(f"First and Last Books Read in {YEAR}")
    # sort the dataframe by My Rating and Average Rating
    books_df = books_df.sort_values(
        by=['Date Read'], ascending=True, ignore_index=True)

    first = books_df.loc[0]
    last = books_df.loc[len(books_df)-1]

    print(tabulate(tabular_data=[first, last],
          headers='keys', tablefmt='fancy_grid'))
    pretty_printer()


def books_read_per_month(books_df: pd.DataFrame):
    # store only the columns we are interested in

    books_df = books_df.loc[:, ['Title', 'Author', 'Date Read']]

    print(f"Books Read Per Month in {YEAR}")
    # sort the dataframe by My Rating and Average Rating
    books_df['Date Read'] = pd.to_datetime(books_df['Date Read'])
    books_df['Month'] = books_df['Date Read'].dt.month

    # get the number of books read per month and include zero values for months that have no books read
    books_per_month = books_df['Month'].value_counts().reindex(
        range(1, 13), fill_value=0)

    # change Month column to be the month name
    books_per_month.index = books_per_month.index.map({1: 'January', 2: 'February', 3: 'March', 4: 'April',
                                                      5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'})

    print(tabulate(tabular_data=books_per_month.to_frame(),
          headers=['Month', 'Books Read'], tablefmt='fancy_grid'))

    pretty_printer()


def tag_distribution(books_df: pd.DataFrame):
    # get only bookshelves column
    books_df = books_df.loc[:, ['Bookshelves']]

    # group by the bookshelves column count
    books_df = books_df.groupby(
        'Bookshelves').size().reset_index(name='counts')

    # sort by counts
    books_df = books_df.sort_values(
        by=['counts'], ascending=False, ignore_index=False)

    print(f"Tag Distribution in {YEAR}")

    print(tabulate(tabular_data=books_df, headers='keys',
                   tablefmt='fancy_grid', showindex=False))
    pretty_printer()


YEAR = 2022
books_df = pd.read_csv('goodreads_library_export.csv', encoding='utf-8',
                       header=0, usecols=['Title', 'Author', 'My Rating', 'Average Rating', 'Publisher', 'Binding', 'Number of Pages', 'Original Publication Year', 'Date Read', 'Bookshelves', 'Exclusive Shelf'])

# get the year from the the Date Read column
books_df['Date Read'] = pd.to_datetime(books_df['Date Read'])
books_df['Year'] = books_df['Date Read'].dt.year

# filter the dataframe to only include the year we are interested in
books_df = books_df[books_df['Year'] == YEAR]

# check if CHECKPOINT1.csv exists
if os.path.exists('CHECKPOINT1.csv'):
    print("CHECKPOINT1.csv exists. Reading from file...")
    books_df = pd.read_csv('CHECKPOINT1.csv', encoding='utf-8', header=0)
else:
    cleanup_dataframe(books_df)


total_books_read(books_df)
top_N_authors(books_df)
top_N_rated_books(books_df)
top_N_publishers(books_df)
average_rating(books_df)
top_N_binding(books_df)
total_pages_read(books_df)
average_pages_read(books_df)
shortest_and_longest_books(books_df)
oldest_book_read(books_df)
first_and_last_books_read(books_df)
books_read_per_month(books_df)
tag_distribution(books_df)
