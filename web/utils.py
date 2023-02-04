import pandas as pd
import os


#######################
# DATA PROCESSING START
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
    books_df.to_csv("CSVs/CHECKPOINT1.csv", index=False, encoding="utf-8")


def prepare_csv():
    # create a dataframe from the csv file
    books_df = pd.read_csv(
        "CSVs/temp.csv",
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
    books_df["Date Read"] = pd.to_datetime(books_df["Date Read"])
    books_df["Year"] = books_df["Date Read"].dt.year

    if not os.path.exists("CSVs/CHECKPOINT1.csv"):
        cleanup_dataframe(books_df)
    books_df = pd.read_csv("CSVs/CHECKPOINT1.csv", encoding="utf-8", header=0)
    return books_df


#######################
# DATA PROCESSING START
#######################


def total_books_read(books_df: pd.DataFrame):
    return len(books_df)


def average_rating(books_df: pd.DataFrame):
    return round(books_df["My Rating"].mean(), 2)


def total_pages_read(books_df: pd.DataFrame):
    totalpgs= books_df["Number of Pages"].sum().astype(int)
    totalpgs = totalpgs/1000
    return round(totalpgs, 2)
    

def average_page_per_book(books_df: pd.DataFrame):
    return books_df["Number of Pages"].mean().astype(int)

def shortest_book(books_df: pd.DataFrame):
    books_df= books_df[books_df["Number of Pages"] == books_df["Number of Pages"].min()]
    shortest_book_name = books_df["Title"].values[0]
    shortest_book_pages = books_df["Number of Pages"].values[0].astype(int)
    return (shortest_book_name, shortest_book_pages)

def longest_book(books_df: pd.DataFrame):
    books_df= books_df[books_df["Number of Pages"] == books_df["Number of Pages"].max()]
    longest_book_name = books_df["Title"].values[0]
    longest_book_pages = books_df["Number of Pages"].values[0].astype(int)
    return (longest_book_name, longest_book_pages)

def oldest_book(books_df: pd.DataFrame):
    books_df["Date Read"] = pd.to_datetime(books_df["Date Read"])
    books_df["Year"] = books_df["Date Read"].dt.year
    books_df= books_df[books_df["Year"] == books_df["Year"].min()]
    oldest_book_name = books_df["Title"].values[0]
    oldest_book_year = books_df["Year"].values[0].astype(int)
    return (oldest_book_name, oldest_book_year)


def top_10_authors(books_df: pd.DataFrame, N: int = 10):
    author_count = books_df["Author"].value_counts().head(N)
    author_count = author_count.to_frame().reset_index()
    author_count.columns = ["Author", "Books Read"]
    return author_count


def top_10_rated_books(books_df: pd.DataFrame, N: int = 10):
    books_df = books_df[books_df["My Rating"] > 0]
    books_df = books_df[["Title", "Author", "My Rating", "Average Rating"]]
    return books_df.sort_values(
        by=["My Rating", "Average Rating"], ascending=False
    ).head(N)


def top_10_publishers(books_df: pd.DataFrame, N: int = 10):
    publisher_count = books_df["Publisher"].value_counts()
    publisher_count = publisher_count[publisher_count > 1]
    publisher_count = publisher_count.head(N).to_frame().reset_index()
    publisher_count.columns = ["Publisher", "Books Read"]
    return publisher_count


def top_10_binding(books_df: pd.DataFrame, N: int = 10):
    binding_count = books_df["Binding"].value_counts()
    binding_count = binding_count[binding_count > 1]
    binding_count= binding_count.head(N).to_frame().reset_index()
    binding_count.columns = ["Format", "Books Read"]
    return binding_count

def books_read_per_year(books_df: pd.DataFrame):
    books_df["Date Read"] = pd.to_datetime(books_df["Date Read"])
    books_df["Year"] = books_df["Date Read"].dt.year
    
    # replace the NaN values in the year column with "Undefined"
    books_df["Year"] = books_df["Year"].fillna("Undefineddd")
    
    # remove the last 2 characters from the year column
    books_df["Year"] = books_df["Year"].astype(str).str[:-2]
    

    books_df = books_df[["Title", "Year"]]
    books_per_year = books_df.groupby("Year").count()
    books_per_year = books_per_year.reset_index()
    books_per_year.columns = ["Year", "Books Read"]
    return books_per_year


def tag_distribution(books_df: pd.DataFrame):
    books_df = books_df.loc[:, ["Bookshelves"]]
    # group by the bookshelves column count
    books_df = books_df.groupby("Bookshelves").size().reset_index(name="counts")
    return books_df.sort_values(by=["counts"], ascending=False, ignore_index=False)
    
    