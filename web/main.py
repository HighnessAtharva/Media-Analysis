from flask import Flask, render_template, request
from utils import *


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    # ON FORM SUBMISSION
    if request.method == "POST":
        if file := request.files["file"]:
            # save the file uploaded by the user to the server
            file.save("CSVs/temp.csv")

            books_df = prepare_csv()

            # start storing the data in variables
            _total_books_read = total_books_read(books_df)
            _average_rating = average_rating(books_df)
            _top_10_authors = top_10_authors(books_df)
            _top_10_rated_books = top_10_rated_books(books_df)
            _top_10_publishers = top_10_publishers(books_df)
            _top_10_binding = top_10_binding(books_df)
            _total_pages_read = total_pages_read(books_df)
            _average_page_per_book= average_page_per_book(books_df)
            _shortest_book, _shortest_book_pages = shortest_book(books_df)[0], shortest_book(books_df)[1]
            _longest_book, _longest_book_pages = longest_book(books_df)[0], longest_book(books_df)[1]
            _oldest_book, _oldest_book_year = oldest_book(books_df)[0], oldest_book(books_df)[1]
            _books_read_per_year = books_read_per_year(books_df)
            _tag_distribution = tag_distribution(books_df)

            return render_template(
                "report.html",
                total_books=_total_books_read,
                average_rating=_average_rating,
                
                total_pages_read=_total_pages_read,
                average_page_per_book=_average_page_per_book,
                shortest_book=_shortest_book,
                shortest_book_pages=_shortest_book_pages,
                
                longest_book=_longest_book,
                longest_book_pages=_longest_book_pages,
                
                oldest_book=_oldest_book,
                oldest_book_year=_oldest_book_year,
                
                top_authors=[_top_10_authors.to_html(classes="top_authors", header=True, index=False)],
                top_books=[_top_10_rated_books.to_html(classes="top_books", header=True, index=False)],
                top_publishers=[_top_10_publishers.to_html(classes="top_publishers", header=True, index=False)],
                top_binding = [_top_10_binding.to_html(classes="top_binding", header=True, index=False)],
                books_read_per_year = [_books_read_per_year.to_html(classes="books_read_per_year", header=True, index=False)],
                tag_distribution = [_tag_distribution.to_html(classes="tag_distribution", header=True, index=False)],
            )

    # ON GET REQUEST
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
