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
    books_df = books_df.dropna(how="all", axis=0)

    # split the title on the first occurence of ( and take the first part
    books_df["Title"] = books_df["Title"].str.split("(", n=1, expand=True)[0]

    # drop the year column since we don't need it anymore
    books_df = books_df.drop(["Year"], axis=1)

    # filter out rows where exclusive shelf value == read
    books_df = books_df[books_df["Exclusive Shelf"] == "read"]

    # strip whitespaces from all rows
    books_df = books_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # write the dataframe to a csv file
    books_df.to_csv("CHECKPOINT1.csv", index=False, encoding="utf-8")


#######################
# DATA ANALYSIS START #
#######################



def books_read_per_month(books_df: pd.DataFrame):
    # store only the columns we are interested in

    books_df = books_df.loc[:, ["Title", "Author", "Date Read"]]

    print(f"Books Read Per Month in {YEAR}")
    # sort the dataframe by My Rating and Average Rating
    books_df["Date Read"] = pd.to_datetime(books_df["Date Read"])
    books_df["Month"] = books_df["Date Read"].dt.month

    # get the number of books read per month and include zero values for months that have no books read
    books_per_month = (
        books_df["Month"].value_counts().reindex(range(1, 13), fill_value=0)
    )

    # change Month column to be the month name
    books_per_month.index = books_per_month.index.map(
        {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December",
        }
    )

    print(
        tabulate(
            tabular_data=books_per_month.to_frame(),
            headers=["Month", "Books Read"],
            tablefmt="fancy_grid",
        )
    )

    pretty_printer()


def tag_distribution(books_df: pd.DataFrame):
    # get only bookshelves column
    books_df = books_df.loc[:, ["Bookshelves"]]

    # group by the bookshelves column count
    books_df = books_df.groupby("Bookshelves").size().reset_index(name="counts")

    # sort by counts
    books_df = books_df.sort_values(by=["counts"], ascending=False, ignore_index=False)

    print(f"Tag Distribution in {YEAR}")

    print(
        tabulate(
            tabular_data=books_df,
            headers="keys",
            tablefmt="fancy_grid",
            showindex=False,
        )
    )
    pretty_printer()


YEAR = 2022
books_df = pd.read_csv(
    "goodreads_library_export.csv",
    encoding="utf-8",
    header=0,
    usecols=[
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
    ],
)

# get the year from the the Date Read column
books_df["Date Read"] = pd.to_datetime(books_df["Date Read"])
books_df["Year"] = books_df["Date Read"].dt.year

# filter the dataframe to only include the year we are interested in
books_df = books_df[books_df["Year"] == YEAR]

# check if CHECKPOINT1.csv exists
if os.path.exists("CHECKPOINT1.csv"):
    print("CHECKPOINT1.csv exists. Reading from file...")
    books_df = pd.read_csv("CHECKPOINT1.csv", encoding="utf-8", header=0)
else:
    cleanup_dataframe(books_df)



total_pages_read(books_df)
average_pages_read(books_df)
shortest_and_longest_books(books_df)
oldest_book_read(books_df)
first_and_last_books_read(books_df)
books_read_per_month(books_df)
tag_distribution(books_df)
