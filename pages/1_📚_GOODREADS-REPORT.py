import pandas as pd
import os
import streamlit as st
import numpy as np
from functools import wraps


def add_seperator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        st.markdown("---")
        return result

    return wrapper


@st.cache_data
def cleanup_dataframe(books_df: pd.DataFrame):
    # check for null values and drop them
    books_df = books_df.dropna(how="all", axis=0)

    # split the title on the first occurence of ( and take the first part
    books_df["Title"] = books_df["Title"].str.split("(", n=1, expand=True)[0]

    # drop the year column since we don't need it anymore
    books_df = books_df.drop(["Year"], axis=1)

    # filter out rows where exclusive shelf value == read
    books_df = books_df[books_df["Exclusive Shelf"] == "read"]

    # strip whitespaces from all rows
    books_df = books_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # check if csvs folder exists
    if not os.path.exists("csvs"):
        os.mkdir("csvs")
        if not os.path.exists("csvs/goodreads"):
            os.mkdir("csvs/goodreads")

    # write the dataframe to a csv file
    books_df.to_csv("csvs/goodreads/CHECKPOINT1.csv", index=False, encoding="utf-8")


@add_seperator
@st.cache_data
def general_stats(books_df: pd.DataFrame):
    col1, col2, col3 = st.columns(3)

    # total number of books read
    with col1:
        st.header("Total :blue[Books] Read")
        st.markdown(f"## {len(books_df)}")

    # total number of pages read
    with col2:
        st.header("Total :green[Pages] Read")
        st.markdown(f"## {books_df['Number of Pages'].sum().astype(int)}")

    # total number of authors read
    with col3:
        st.header("Total :red[Authors] Read")
        st.markdown(f"## {len(books_df['Author'].unique())}")


@add_seperator
@st.cache_data
def total_books_by_year(books_df: pd.DataFrame):
    st.header("Total Books Read by Year")

    # add a new column to the dataframe that contains the year of the book
    books_df["Year"] = books_df["Date Read"].str.split("-", n=1, expand=True)[0]

    # count the number of books read by each year
    books_by_year = books_df["Year"].value_counts()
    books_by_year = books_by_year.sort_index()

    st.area_chart(books_by_year)


# TODO: display the bar graph from highest to lowest
@add_seperator
@st.cache_data
def top_N_authors(books_df: pd.DataFrame, num_authors: int, genre: str, year: int):
    # for all genres and all years
    if genre == "All" and year == "All":
        st.markdown(f"### Top {num_authors} Authors")
        author_count = books_df[
            "Author"
        ].value_counts()  # count the number of books read by each author
        author_count = author_count[author_count > 1]
        if author_count.empty:
            st.error("Not enough authors to display")
        else:
            st.bar_chart(author_count.head(num_authors))

    # for specific genre and all years
    if genre != "All" and year == "All":
        st.markdown(f"### Top {num_authors} Authors in {genre.upper()} bookshelf")
        author_count = books_df[books_df["Bookshelves"] == genre][
            "Author"
        ].value_counts()  # count the number of books read by each author
        author_count = author_count[author_count > 1]
        if author_count.empty:
            st.error("Not enough authors to display")
        else:
            st.bar_chart(author_count.head(num_authors))

    # for all genres and specific year
    if year != "All" and genre == "All":
        st.markdown(f"### Top {num_authors} Authors in {year}")
        author_count = books_df[books_df["Year"] == year][
            "Author"
        ].value_counts()  # count the number of books read by each author
        author_count = author_count[author_count > 1]
        if author_count.empty:
            st.error("Not enough authors to display")
        else:
            st.bar_chart(author_count.head(num_authors))

    # for specific genre and specific year
    if year != "All" and genre != "All":
        st.markdown(f"### Top Authors in {genre.upper()} bookshelf in {year}")
        author_count = books_df[
            (books_df["Year"] == year) & (books_df["Bookshelves"] == genre)
        ]["Author"].value_counts()
        author_count = author_count[author_count > 1]
        if author_count.empty:
            st.error("Not enough authors to display")
        else:
            st.bar_chart(author_count.head(num_authors))



@add_seperator
def top_N_rated_books(books_df: pd.DataFrame, N: int):
    books_df = books_df[books_df['My Rating'] > 0]
    # store only the columns we are interested in
    books_df = books_df[['Title', 'Author', 'My Rating', 'Average Rating']]

    # sort the dataframe by My Rating and Average Rating
    books_df = books_df.sort_values(
        by=['My Rating', 'Average Rating'], ascending=False)
    
    # replace the index column with the book title
    books_df = books_df.set_index('Title')
    
    # display the top N books
    st.markdown(f"### Top {N} Rated Books")
    st.dataframe(books_df.head(N), use_container_width=True)


# def top_N_publishers(books_df: pd.DataFrame, N: int = 10):
#     print(f"Top {N} Publishers in {YEAR}")
#     # count the number of books read by each author should be greater than 1
#     publisher_count = books_df['Publisher'].value_counts()
#     publisher_count = publisher_count[publisher_count > 1]
#     if N > len(publisher_count):
#         print(
#             f"WARNING: N is greater than the number of publishers in the dataframe. Setting N to {len(publisher_count)}")
#     print(tabulate(tabular_data=publisher_count.head(N).to_frame(),
#           headers=['Publisher', 'Books Read'], tablefmt='fancy_grid'))
#


# def average_rating(books_df: pd.DataFrame):
#     print(f"Average Rating of Books Read in {YEAR}")
#     # count the number of books read by each author should be greater than 1
#     avg_rating = books_df['My Rating'].mean()
#     print(tabulate(tabular_data=[[avg_rating]], headers=[
#           'Average Rating'], tablefmt='fancy_grid'))
#


# def top_N_binding(books_df: pd.DataFrame, N: int = 10):
#     print(f"Top {N} Binding Types in {YEAR}")
#     # count the number of books read by each author should be greater than 1
#     binding_count = books_df['Binding'].value_counts()
#     binding_count = binding_count[binding_count > 1]
#     if N > len(binding_count):
#         print(
#             f"WARNING: N is greater than the number of bindings in the dataframe. Setting N to {len(binding_count)}")
#     print(tabulate(tabular_data=binding_count.head(N).to_frame(),
#           headers=['Binding', 'Books Read'], tablefmt='fancy_grid'))
#


# def total_pages_read(books_df: pd.DataFrame):
#     print(f"Total Pages Read in {YEAR}")
#     # count the number of books read by each author should be greater than 1
#     total_pages = books_df['Number of Pages'].sum()
#     print(tabulate(tabular_data=[[total_pages]], headers=[
#           'Total Pages'], tablefmt='fancy_grid'))
#


# def average_pages_read(books_df: pd.DataFrame):
#     print(f"Average Pages Read in {YEAR}")
#     # count the number of books read by each author should be greater than 1
#     avg_pages = books_df['Number of Pages'].mean()
#     print(tabulate(tabular_data=[[avg_pages]], headers=[
#           'Average Pages'], tablefmt='fancy_grid'))
#


# def shortest_and_longest_books(books_df: pd.DataFrame):
#     # store only the columns we are interested in
#     books_df = books_df[['Title', 'Author', 'Number of Pages']]

#     print(f"Shortest and Longest Books Read in {YEAR}")
#     # sort the dataframe by My Rating and Average Rating
#     books_df = books_df.sort_values(
#         by=['Number of Pages'], ascending=True, ignore_index=True)

#     smallest = books_df.loc[0]
#     largest = books_df.loc[len(books_df)-1]

#     print(tabulate(tabular_data=[smallest, largest],
#           headers='keys', tablefmt='fancy_grid'))
#


# def oldest_book_read(books_df: pd.DataFrame):
#     # store only the columns we are interested in
#     books_df = books_df[['Title', 'Author', 'Original Publication Year']]

#     print(f"Oldest Book Read in {YEAR}")
#     # sort the dataframe by My Rating and Average Rating
#     books_df = books_df.sort_values(
#         by=['Original Publication Year'], ascending=True, ignore_index=True)

#     oldest = books_df.loc[0]

#     print(tabulate(tabular_data=[oldest],
#           headers='keys', tablefmt='fancy_grid'))
#


# def first_and_last_books_read(books_df: pd.DataFrame):
#     # store only the columns we are interested in
#     books_df = books_df[['Title', 'Author', 'Date Read']]

#     print(f"First and Last Books Read in {YEAR}")
#     # sort the dataframe by My Rating and Average Rating
#     books_df = books_df.sort_values(
#         by=['Date Read'], ascending=True, ignore_index=True)

#     first = books_df.loc[0]
#     last = books_df.loc[len(books_df)-1]

#     print(tabulate(tabular_data=[first, last],
#           headers='keys', tablefmt='fancy_grid'))
#


# def books_read_per_month(books_df: pd.DataFrame):
#     # store only the columns we are interested in

#     books_df = books_df.loc[:, ['Title', 'Author', 'Date Read']]

#     print(f"Books Read Per Month in {YEAR}")
#     # sort the dataframe by My Rating and Average Rating
#     books_df['Date Read'] = pd.to_datetime(books_df['Date Read'])
#     books_df['Month'] = books_df['Date Read'].dt.month

#     # get the number of books read per month and include zero values for months that have no books read
#     books_per_month = books_df['Month'].value_counts().reindex(
#         range(1, 13), fill_value=0)

#     # change Month column to be the month name
#     books_per_month.index = books_per_month.index.map({1: 'January', 2: 'February', 3: 'March', 4: 'April',
#                                                       5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'})

#     print(tabulate(tabular_data=books_per_month.to_frame(),
#           headers=['Month', 'Books Read'], tablefmt='fancy_grid'))

#


# def tag_distribution(books_df: pd.DataFrame):
#     # get only bookshelves column
#     books_df = books_df.loc[:, ['Bookshelves']]

#     # group by the bookshelves column count
#     books_df = books_df.groupby(
#         'Bookshelves').size().reset_index(name='counts')

#     # sort by counts
#     books_df = books_df.sort_values(
#         by=['counts'], ascending=False, ignore_index=False)

#     print(f"Tag Distribution in {YEAR}")

#     print(tabulate(tabular_data=books_df, headers='keys',
#                    tablefmt='fancy_grid', showindex=False))
#


# CONFIG
st.set_page_config(
    page_title="Goodreads Analysis",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# TITLE
st.title(":blue[Goodreads] Reading Analysis :book:")

# FILE UPLOAD WIDGET
uploaded_file = st.file_uploader(
    label="Choose a Goodreads Export CSV File",
    type=["csv"],
    help="Goodreads Account -> Settings -> Export",
    accept_multiple_files=False,
)


if uploaded_file is not None:
    books_df = pd.read_csv(uploaded_file, encoding="utf-8", header=0)

    # check if dataframe is valid by checking for columns
    # TODO: Add other columns here later
    if (
        "Title" in books_df.columns
        and "Author" in books_df.columns
        and "Exclusive Shelf" in books_df.columns
    ):
        st.success("File Uploaded Successfully! Proceeding to Data Analysis.")
        books_df = books_df[
            [
                "Title",
                "Author",
                "My Rating",
                "Average Rating",
                "Publisher",
                "Binding",
                "Number of Pages",
                "Original Publication Year",
                "Date Read",
                "Bookshelves",
                "Exclusive Shelf",
            ]
        ]

        # get the year from the the Date Read column
        books_df["Date Read"] = pd.to_datetime(books_df["Date Read"])
        books_df["Year"] = books_df["Date Read"].dt.year

        # check if csvs/goodreads folder exists and file CHECKPOINT1.csv exists, if not then run cleanup_dataframe
        if not os.path.exists("csvs/goodreads/CHECKPOINT1.csv"):
            cleanup_dataframe(books_df)

        books_df = pd.read_csv(
            "csvs/goodreads/CHECKPOINT1.csv", encoding="utf-8", header=0
        )
        # st.header("Data Preview")
        # st.dataframe(books_df)
        # st.markdown("---")

        # GENERAL STATS
        general_stats(books_df)

        # BOOKS READ PER YEAR
        total_books_by_year(books_df)

        # AUTHOR STATS
        st.header("Most Read Authors")
        col1, col2, col3 = st.columns(3)

        with col1:
            max_authors = len(books_df["Author"].unique())
            max_authors = min(max_authors, 20)
            num_authors = st.slider(
                label="Select Number of Authors",
                min_value=1,
                max_value=max_authors,
                value=5,
                step=1,
            )

        with col2:

            genres = books_df["Bookshelves"].unique()  # show a dropdown by genre
            genres = [genre for genre in genres if genre != "to-read"]
            genres = [genre for genre in genres if genre != "currently-reading"]
            genre = st.selectbox(
                label="Filter by Shelf", options=["All"] + genres, index=0
            )

        with col3:
            books_df["Year"] = books_df["Date Read"].str.split("-", n=1, expand=True)[
                0
            ]  # show a dropdown by year of reading
            years = books_df["Year"].unique()
            years = years[~pd.isnull(years)]  # drop all rows with NaN values
            years = np.insert(years, 0, "All")  # add a 'All' as first option
            year = st.selectbox(label="Filter by Year", options=years, index=0)

        top_N_authors(books_df, num_authors, genre, year)
        
        # TOP N BOOKS
        st.header("Top Books by Rating")
        book_count = len(books_df["Title"].unique())
        book_count = min(book_count, 25)
        book_count = range(10, book_count + 1, 5)
        num_books = st.selectbox(label="Limit By", options=book_count, index=0)
        top_N_rated_books(books_df, num_books)
        
        # total_books_read(books_df)
        # top_N_authors(books_df)
        # top_N_rated_books(books_df)
        # top_N_publishers(books_df)
        # average_rating(books_df)
        # top_N_binding(books_df)
        # total_pages_read(books_df)
        # average_pages_read(books_df)
        # shortest_and_longest_books(books_df)
        # oldest_book_read(books_df)
        # first_and_last_books_read(books_df)
        # books_read_per_month(books_df)
        # tag_distribution(books_df)

    else:
        st.error("Invalid CSV File. Please upload a valid Goodreads CSV File.")


# #######################
# # DATA ANALYSIS START #
# #######################


# def :
#     print("""
#           ----------------8<-------------[ Annual Book Report ]------------------
#           """)


# YEAR = 2022
# books_df = pd.read_csv('goodreads_export.csv', encoding='utf-8',
#                        header=0, usecols=['Title', 'Author', 'My Rating', 'Average Rating', 'Publisher', 'Binding', 'Number of Pages', 'Original Publication Year', 'Date Read', 'Bookshelves', 'Exclusive Shelf'])

# # get the year from the the Date Read column
# books_df['Date Read'] = pd.to_datetime(books_df['Date Read'])
# books_df['Year'] = books_df['Date Read'].dt.year

# # filter the dataframe to only include the year we are interested in
# books_df = books_df[books_df['Year'] == YEAR]

# # check if CHECKPOINT1.csv exists
# if os.path.exists('CHECKPOINT1.csv'):
#     print("CHECKPOINT1.csv exists. Reading from file...")
#     books_df = pd.read_csv('CHECKPOINT1.csv', encoding='utf-8', header=0)
# else:
#     cleanup_dataframe(books_df)


# total_books_read(books_df)
# top_N_authors(books_df)
# top_N_rated_books(books_df)
# top_N_publishers(books_df)
# average_rating(books_df)
# top_N_binding(books_df)
# total_pages_read(books_df)
# average_pages_read(books_df)
# shortest_and_longest_books(books_df)
# oldest_book_read(books_df)
# first_and_last_books_read(books_df)
# books_read_per_month(books_df)
# tag_distribution(books_df)
