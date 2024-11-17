from flask import Flask, jsonify, request
from http import HTTPStatus

app = Flask(__name__)

books = [
    {
        "id": 1,
        "title": "Patayin sa shokot si remington",
        "author": "Frank Abagnale",
        "year": 1999,
    },
    {"id": 2, "title": "1984", "author": "Abraham Dimagiba", "year": 1969},
]


def find_book(book_id):
    return next((book for book in books if book["id"] == book_id), None)


@app.route("/")
def hello_user():
    return "Hello, Client!"


@app.route("/api/books", methods=["GET"])
def get_books():
    return jsonify({"success": True, "data": books, "total": len(books)}), HTTPStatus.OK


@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = find_book(book_id)
    if book is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Book not found",
                }
            ),
            HTTPStatus.NOT_FOUND,
        )
    return (
        jsonify(
            {
                "success": True,
                "data": book,
            }
        ),
        HTTPStatus.OK,
    )


@app.route("/api/books", methods=["POST"])
def create_book():
    if not request.is_json:
        return (
            jsonify(
                {"success": False, "error": "Content-type must be application/json"}
            ),
            HTTPStatus.BAD_REQUEST,
        )

    data = request.get_json()

    required_fields = ["title", "author", "year"]
    for field in required_fields:
        if field not in data:
            return (
                jsonify(
                    {"success": False, "error": f"Missing required fields: {field}"}
                ),
                HTTPStatus.BAD_REQUEST,
            )

    new_book = {
        "id": max(book["id"] for book in books) + 1,
        "title": data["title"],
        "author": data["author"],
        "year": data["year"],
    }

    books.append(new_book)

    return jsonify({"success": True, "data": new_book}), HTTPStatus.CREATED


@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = find_book(book_id)
    if book is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Book not found",
                }
            ),
            HTTPStatus.NOT_FOUND,
        )
    if not request.is_json:
        return (
            jsonify(
                {"success": False, "error": "Content-type must be application/json"}
            ),
            HTTPStatus.BAD_REQUEST,
        )
    
    data = request.get_json()

    allowed_fields = ["title", "author", "year"]
    for field in data:
        if field not in allowed_fields:
            return (
                jsonify(
                    {"success": False, "error": f"Invalid field: {field}"}
                ),
                HTTPStatus.BAD_REQUEST,
            )

    book.update(data)

    return jsonify({"success": True, "data": book}), HTTPStatus.OK


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = find_book(book_id)
    if book is None:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Book not found",
                }
            ),
            HTTPStatus.NOT_FOUND,
        )

    books.remove(book)

    return jsonify({"success": True, "message": f"Book with id {book_id} deleted"}), HTTPStatus.OK


@app.errorhandler(404)
def not_found(error):
    return (
        jsonify({"succcess": False, "error": "Resource not found"}),
        HTTPStatus.NOT_FOUND,
    )


@app.errorhandler(500)
def not_found(error):
    return (
        jsonify({"succcess": False, "error": "Internal Server Error"}),
        HTTPStatus.INTERNAL_SERVER_ERROR,
    )


if __name__ == "__main__":
    app.run(debug=True)
