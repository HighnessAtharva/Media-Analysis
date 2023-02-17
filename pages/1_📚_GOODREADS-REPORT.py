import pandas as pd
import os
import streamlit as st
import numpy as np
from functools import wraps
from datetime import datetime
import altair as alt
import calendar
import requests

def add_seperator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        st.markdown("---")
        return result
    return wrapper

def get_book_cover(bookISBN):
    bookISBN = bookISBN[:-2]
    book_cover = f"https://covers.openlibrary.org/b/isbn/{bookISBN}-L.jpg"
    if len(bookISBN) == 13 and len(requests.get(book_cover).content) > 1000:
        return book_cover
    else:
        return "https://islandpress.org/sites/default/files/default_book_cover_2015.jpg"
    
      
def cleanup_dataframe(books_df: pd.DataFrame):
    books_df = books_df.dropna(how="all", axis=0) # check for null values and drop them
    books_df["Title"] = books_df["Title"].str.split("(", n=1, expand=True)[0] # split the title on the first occurence of ( and take the first part
    books_df = books_df[books_df["Exclusive Shelf"] == "read"] # filter out rows where exclusive shelf value == read
    books_df = books_df.apply(lambda x: x.str.strip() if x.dtype == "object" else x) # strip whitespaces from all rows
    books_df["ISBN13"] = books_df["ISBN13"].str[2:-1] # strip first two and last one characters from ISBN13 and convert to int
    
    # check if csvs folder exists
    if not os.path.exists("csvs"):
        os.mkdir("csvs")
        if not os.path.exists("csvs/goodreads"):
            os.mkdir("csvs/goodreads")
    
    books_df.to_csv("csvs/goodreads/CHECKPOINT1.csv", index=False, encoding="utf-8") # write the dataframe to a csv file

@add_seperator
@st.cache_data
def general_stats(books_df: pd.DataFrame):
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Total :blue[Books] Read")
        st.markdown(f"## {len(books_df)}")
    with col2:
        st.header("Total :green[Pages] Read")
        st.markdown(f"## {books_df['Number of Pages'].sum().astype(int)}")
    with col3:
        st.header("Total :red[Authors] Read")
        st.markdown(f"## {len(books_df['Author'].unique())}")
    col1, col2, col3 = st.columns(3)

@add_seperator
@st.cache_data
def total_books_by_year(books_df: pd.DataFrame):
    st.header("Total Books Read by Year 🗓️")
    books_by_year = books_df["Year"].value_counts()
    books_by_year = books_by_year[books_by_year.index != ""]
    books_by_year = books_by_year.sort_index().astype(int)
    st.bar_chart(books_by_year)

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
        
        if author_count.empty or len(author_count) < num_authors:
            st.error("Not enough authors to in your library")
        else:
            
            chart = alt.Chart(author_count.head(num_authors).reset_index()).mark_bar().encode(
                x=alt.X('index', sort='-y'),
                y='Author',
                color='Author'
            )
            st.altair_chart(chart, use_container_width=True)
        
    # for specific genre and all years
    if genre != "All" and year == "All":
        st.markdown(f"### Top {num_authors} Authors in {genre.upper()} bookshelf")
        author_count = books_df[books_df["Bookshelves"] == genre][
            "Author"
        ].value_counts()  # count the number of books read by each author
        author_count = author_count[author_count > 1]
        if author_count.empty or len(author_count) < num_authors:
            st.error("Not enough authors to display for the given genre")
        else:
            chart = alt.Chart(author_count.head(num_authors).reset_index()).mark_bar().encode(
                x=alt.X('index', sort='-y'),
                y='Author',
                color='Author'
            )
            st.altair_chart(chart, use_container_width=True)
            
    # for all genres and specific year
    if year != "All" and genre == "All":
        st.markdown(f"### Top {num_authors} Authors in {year}")
        author_count = books_df[books_df["Year"] == year][
            "Author"
        ].value_counts()  # count the number of books read by each author
        author_count = author_count[author_count > 1]
        if author_count.empty or len(author_count) < num_authors:
            st.error("Not enough authors to display for the given year")
        else:
            chart = alt.Chart(author_count.head(num_authors).reset_index()).mark_bar().encode(
                x=alt.X('index', sort='-y'),
                y='Author',
                color='Author'
            )
            st.altair_chart(chart, use_container_width=True)
            
    # for specific genre and specific year
    if year != "All" and genre != "All":
        st.markdown(f"### Top Authors in {genre.upper()} bookshelf in {year}")
        author_count = books_df[
            (books_df["Year"] == year) & (books_df["Bookshelves"] == genre)
        ]["Author"].value_counts()
        author_count = author_count[author_count > 1]
        if author_count.empty or len(author_count) < num_authors:
            st.error("Not enough authors to display for the given year and genre")
        else:
            chart = alt.Chart(author_count.head(num_authors).reset_index()).mark_bar().encode(
                x=alt.X('index', sort='-y'),
                y='Author',
                color='Author'
            )
            st.altair_chart(chart, use_container_width=True)

@add_seperator
def top_N_rated_books(books_df: pd.DataFrame, N: int):
    books_df = books_df[books_df["My Rating"] > 0]
    books_df = books_df[["Title", "Author", "My Rating", "Average Rating"]] # store only the columns we are interested in
    books_df = books_df.sort_values(by=["My Rating", "Average Rating"], ascending=False) # sort the dataframe by My Rating and Average Rating
    books_df = books_df.set_index("Title") 
    st.markdown(f"### Top {N} Rated Books") 
    st.dataframe(books_df.head(N), use_container_width=True)

@add_seperator
def bottom_N_rated_books(books_df: pd.DataFrame, N: int):
    books_df = books_df[books_df["My Rating"] > 0]
    books_df = books_df[["Title", "Author", "My Rating", "Average Rating"]]
    books_df = books_df.sort_values(by=["My Rating", "Average Rating"], ascending=True)
    books_df = books_df.set_index("Title")
    st.markdown(f"### Bottom {N} Rated Books")
    st.dataframe(books_df.head(N), use_container_width=True)

@st.cache_data
@add_seperator
def total_pages_per_year(books_df: pd.DataFrame):
    st.markdown("### Total Pages Read per Year")
    books_df = books_df[books_df["Year"] != ""] # drop all nans
    books_df = books_df.dropna()
    books_df["Year"] = books_df["Year"].astype(int)
    books_df = books_df.groupby("Year").sum().astype(int) # sum the number of pages read per year
    books_df = books_df["Number of Pages"]
    st.line_chart(books_df, y="Number of Pages")

@st.cache_data
@add_seperator
def average_rating_per_year(books_df: pd.DataFrame):
    st.markdown("### Average Rating per Year") # do a time series plot of average rating per year
    books_df = books_df[books_df["Year"] != ""]
    books_df = books_df.dropna()
    books_df["Year"] = books_df["Year"].astype(int)
    books_df = books_df.groupby("Year").mean()
    books_df = books_df["Average Rating"]
    st.line_chart(books_df, y="Average Rating")

# @st.cache_data
@add_seperator
def pages_read_per_month(books_df: pd.DataFrame):
    st.markdown("### Pages Read per Month (Yearly Comparison)")
    books_df = books_df[books_df["Year"] != ""]
    books_df = books_df.dropna() # drop all nans
    books_df["Month"] = books_df["Date Read"].apply(lambda x: x.split("-")[1])
    books_df = books_df[["Number of Pages", "Year", "Month"]] # keep only pages, year and month
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"] # add rows for months that are not present in the dataset and set the number of pages to 0
    years = books_df["Year"].unique()
    for year in years:
        for month in months:
            if month not in books_df[books_df["Year"] == year]["Month"].unique():
                books_df = books_df.append(
                    {"Number of Pages": 0, "Year": year, "Month": month},
                    ignore_index=True,
                )
    
    grouped = books_df.groupby(["Year", "Month"]).agg({"Number of Pages": "sum"}) # Group the data by year and month and sum the number of pages read
    grouped = grouped.reset_index() # change the x axis values to add month name next to the month number
    grouped["Month"] = grouped["Month"].apply(
        lambda x: f"{str(x)}-" + calendar.month_name[int(x)]
    )
    
    # plot the altair chart with x as month and y as number of pages with a line for each year in the multi-series line chart
    st.altair_chart(
        alt.Chart(grouped.reset_index())
        .mark_line()
        .encode(
            x="Month",
            y="Number of Pages",
            color="Year",
            tooltip=["Year", "Month", "Number of Pages"],
        )
        .interactive(),
        use_container_width=True,
        theme="streamlit",
    )
    # st.write(grouped)
    
    
@st.cache_data
@add_seperator
def general_stats_2(books_df: pd.DataFrame):
    col1, col2, col3, col4 = st.columns(4, gap="large")
    with col1:
        st.header(":blue[Oldest] Book Read")
        books_df1 = books_df[["Title", "Original Publication Year"]]
        books_df1 = books_df.sort_values(
            by=["Original Publication Year"], ascending=True, ignore_index=True
        )  # sort the dataframe by My Rating and Average Rating
        oldest = books_df1["Title"][0]
        oldest_pub_year = books_df1["Original Publication Year"][0].astype(int)
        st.markdown(f"### {oldest}")
        st.markdown(f"Published ***{oldest_pub_year}***")
        
        
    with col2:
        isbn = str(books_df[books_df["Title"] == oldest]["ISBN13"].values[0])
        image = get_book_cover(isbn)
        st.image(image,width=150)
    
    
    with col3:
        st.header(":green[Newest] Book Read")
        books_df2 = books_df[["Title", "Original Publication Year"]]
        books_df2 = books_df.sort_values(
            by=["Original Publication Year"], ascending=False, ignore_index=True
        )  # sort reverse by Original Publication Year
        newest = books_df2["Title"][0]
        newest_pub_year = books_df2["Original Publication Year"][0].astype(int)
        st.markdown(f"### {newest}")
        st.markdown(f"Published ***{newest_pub_year}***")
     
    with col4:   
        
        isbn = str(books_df[books_df["Title"] == newest]["ISBN13"].values[0])
        image = get_book_cover(isbn)
        st.image(image,width=150)
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4, gap="large")
    with col1:
        st.header(":red[First] Book Read")
        books_df3 = books_df[["Title", "Author", "Date Read"]]
        books_df3 = books_df3.sort_values(
            by=["Date Read"], ascending=True, ignore_index=True
        )  # sort the dataframe by Date Read
        first = books_df3.loc[0, "Title"]
        date_of_first = books_df3["Date Read"][0]
        date_of_first = datetime.strptime(date_of_first, "%Y-%m-%d").strftime("%B %d, %Y")
        st.markdown(f"### {first}")
        st.markdown(f"Read on ***{date_of_first}***")
        
    with col2: 
        isbn = str(books_df[books_df["Title"] == first]["ISBN13"].values[0])
        image = get_book_cover(isbn)
        st.image(image,width=150)
    
    with col3:
        st.header(":violet[Last] Book Read")
        books_df4 = books_df[["Title", "Author", "Date Read"]]
        books_df4 = books_df4.sort_values(
            by=["Date Read"], ascending=False, ignore_index=True
        )  # sort the dataframe by My Rating and Average Rating
        last = books_df4.loc[0, "Title"]
        date_of_last = books_df4["Date Read"][0]
        date_of_last = datetime.strptime(date_of_last, "%Y-%m-%d").strftime("%B %d, %Y")
        st.markdown(f"### {last}")
        st.markdown(f"Read on ***{date_of_last}***")
    
    with col4:
        isbn = str(books_df[books_df["Title"] == last]["ISBN13"].values[0])
        image = get_book_cover(isbn)
        st.image(image,width=150)
        
        
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4, gap="large")
    with col1:
        st.header(":orange[Longest] Book Read")
        books_df5 = books_df[["Title", "Author", "Number of Pages"]]
        books_df5 = books_df5.sort_values(by=["Number of Pages"], ascending=False, ignore_index=True)  # sort the dataframe by Number of Pages
        longest = books_df5.loc[0, "Title"]
        longest_pages = books_df5["Number of Pages"][0].astype(int)
        st.markdown(f"### {longest}")
        st.markdown(f"A whopping ***{longest_pages}*** pages")
        
    with col2:
        isbn = str(books_df[books_df["Title"] == longest]["ISBN13"].values[0])
        image = get_book_cover(isbn)
        st.image(image,width=150)
    
    with col3:
        st.header(":green[Shortest] Book Read")
        books_df6 = books_df[["Title", "Author", "Number of Pages"]]
        books_df6 = books_df6.sort_values(
            by=["Number of Pages"], ascending=True, ignore_index=True
        )
        shortest = books_df6.loc[0, "Title"]
        shortest_pages = books_df6["Number of Pages"][0].astype(int)
        st.markdown(f"### {shortest}")
        st.markdown(f"A mere ***{shortest_pages}*** pages")
    
    with col4:
        isbn = str(books_df[books_df["Title"] == shortest]["ISBN13"].values[0])
        image = get_book_cover(isbn)
        st.image(image,width=150)
    
        
def top_10_publishers(books_df: pd.DataFrame):
    st.header("Top 10 :blue[Publishers]")
    publisher_count = books_df["Publisher"].value_counts()
    publisher_count = publisher_count[publisher_count > 1]
    publisher_count.index.name = "Publisher"
    publisher_count.name = "Count"
    if len(publisher_count) >= 10:
        st.dataframe(publisher_count.head(10).to_frame(), width=300)
    else:
        st.dataframe(publisher_count.head(len(publisher_count)).to_frame(), width=300)
    
def top_bindings(books_df: pd.DataFrame):
    st.header("Top 10 :blue[Bindings]")
    binding_count = books_df["Binding"].value_counts()
    binding_count = binding_count[binding_count > 1]
    binding_count.index.name = "Binding"
    binding_count.name = "Count"
    st.dataframe(binding_count.head(len(binding_count)).to_frame(), width=300)


def rating_distribution(books_df: pd.DataFrame):
    st.header("Rating Distribution 🎯")
    rating_count = books_df["My Rating"].value_counts()
    rating_count = rating_count[rating_count > 1]
    rating_count.index.name = "Rating"
    rating_count.name = "Count"
    
    chart = alt.Chart(rating_count.to_frame().reset_index()).mark_bar().encode(
        y=alt.Y("Rating:N", axis=alt.Axis(title="Rating")),
        x=alt.X("Count:Q", axis=alt.Axis(title="Count")),
        tooltip=[alt.Tooltip("Count:Q")]
    ).properties(
        width=500,
        height=450
    )
    chart.configure_axisX(labelAngle=0)
    st.altair_chart(chart, use_container_width=True)
     
     

####################
## MAIN FUNCTION  ##
####################

# CONFIG
st.set_page_config(
    page_title="Goodreads Analysis",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# TITLE
st.title(":blue[Goodreads] Reading Analysis :book:")

# INTRO
st.markdown(
    """   
    Are you a bookworm who loves using Goodreads to keep track of your reading progress and discover new books to read? If so, then you're in luck! Introducing the Goodreads Analysis Report tool, the ultimate solution for getting the most out of your Goodreads data. 🤓
    ### How it Works
    With the Goodreads Analysis Report, you simply upload your export CSV file from your Goodreads account and let the tool do the rest! Our tool uses advanced data analysis techniques to generate statistical reports and provide you with in-depth insights that are not available on the Goodreads platform. 📈
    ### Features
    - Analyze Your Reading Data: Our tool provides detailed statistics on the books you've read, including the number of books you've read, the average rating, and the number of pages read.
    - Discover Your Reading Habits: The Goodreads Analysis Report helps you understand your reading habits by providing information on the genres, authors, and publication years of the books you've read.
    - Interactive Dashboards: The tool provides interactive dashboards that allow you to filter your data and explore your reading patterns visually. 
    - Personalized Recommendations: Based on your reading history, the tool provides personalized recommendations for books that you might enjoy, making it easy to discover your next favorite read. 📚
    ### How to Get Started
    To get started with the Goodreads Analysis Report, simply export your Goodreads data as a CSV file and upload it to our tool. From there, our tool will analyze your data and provide you with a comprehensive report on your reading habits. 
    So what are you waiting for? Try out the Goodreads Analysis Report today and start getting the most out of your reading data! 🚀
    """
)

st.write("---")

col1, col2 = st.columns(2, gap="large")
with col1:
    st.info(
        "Don't have a Goodreads account? Create one [here](https://www.goodreads.com/user/sign_up)"
    )
    just_show_me_the_app = st.button("Use the DEMO CSV and skip the upload step")

with col2:
    st.info("Don't have a Goodreads export file? Get an example one below 👇🏻")
    with open("pages/goodreads_export.csv", "rb") as goodreads_example:
        btn = st.download_button(
            label="Download Goodreads Export Example",
            data=goodreads_example,
            file_name="goodreads_export.csv",
            mime="text/csv",
            help="This is an example Goodreads export file. You can use this to test out the app.",
        )

st.write("---")
# FILE UPLOAD WIDGET
uploaded_file = st.file_uploader(
    label="Choose a Goodreads Export CSV File",
    type=["csv"],
    help="Goodreads Account -> Settings -> Export",
    accept_multiple_files=False,
)

if uploaded_file is not None or just_show_me_the_app:
    if just_show_me_the_app:
        uploaded_file = "pages/goodreads_export.csv"
    books_df = pd.read_csv(uploaded_file, encoding="utf-8", header=0)
    
    # check if dataframe is valid by checking for columns
    cols_to_check = ["Title","Author","My Rating","Average Rating","Publisher","Binding","Number of Pages","Original Publication Year","Date Read","Bookshelves","Exclusive Shelf","ISBN13"]
    
    if set(cols_to_check).issubset(set(books_df.columns)):   
        st.success("File Uploaded Successfully! Proceeding to Data Analysis.")
        books_df = books_df[cols_to_check]
       
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
        best, worst = st.columns(2, gap="large")
        
        # FAVORITE N BOOKS BY RATING
        with best:
            st.header(":green[Favorite] Books by Rating ⭐")
            book_count = len(books_df["Title"].unique())
            book_count = min(book_count, 25)
            book_count = range(10, book_count + 1, 5)
            num_books = st.selectbox(
                label="Limit By", options=book_count, index=0, key="fav"
            )
            top_N_rated_books(books_df, num_books)
        
        # LEAST FAVORITE N BOOKS BY RATING
        with worst:
            st.header(":red[Worst] Books by Rating 💩")
            book_count = len(books_df["Title"].unique())
            book_count = min(book_count, 25)
            book_count = range(10, book_count + 1, 5)
            num_books = st.selectbox(
                label="Limit By", options=book_count, index=0, key="least"
            )
            bottom_N_rated_books(books_df, num_books)
        
        # BOOKS READ PER YEAR
        total_books_by_year(books_df)
        
        # AUTHOR STATS
        st.header("Most Read Authors 👨🏻‍🏫")
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
            # sort the numpy years in descending order
            years = np.sort(years)[::-1]
            years = np.insert(years, 0, "All")  # add a 'All' as first option
            year = st.selectbox(
                label="Filter by Year", options=years, index=0, key="totalbooksbyyear"
            )
        
        top_N_authors(books_df, num_authors, genre, year)
        
        # PER YEAR STATS
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.header("Total Pages Read Per Year 📖")
            total_pages_per_year(books_df)
        with col2:
            st.header("Average Rating Per Year ⌚")
            average_rating_per_year(books_df)
        
        # MONTH WISE STATS
        st.header("Month-Wise Reading Trend 📚")
        years = years[1:] # remove "All" from years
        year = st.selectbox(label="Select Year", options=years, index=0, key="monthwisereadingtrend")
        
        pages_read_per_month(books_df)
        
        general_stats_2(books_df)
        
        # PUBLISHER, RATING DISTRIBUTION AND BINDING STATS
        publisher_count = len(books_df["Publisher"].unique())
        max_publishers = min(publisher_count, 20)
        col1, col2, col3 = st.columns([1,2,1], gap="large")
        with col1:
            top_10_publishers(books_df)
        with col2:
            rating_distribution(books_df)       
        with col3:
            top_bindings(books_df)
            
    else:
        st.error("Invalid CSV File. Please upload a valid Goodreads CSV File.")
