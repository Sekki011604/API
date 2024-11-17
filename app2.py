from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost:3306/bookings'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=False)


def find_book(book_id):
    return Book.query.get(book_id)

@app.route("/")
def hello_user():
    return "Hello, User!"

@app.route("/api/books", methods=["GET"])
def get_books():
    books = Book.query.all()
    books_data = [{"id": book.id, "title": book.title, "author": book.author, "year": book.year} for book in books]
    return jsonify({"success": True, "data": books_data, "total": len(books_data)}), HTTPStatus.OK


@app.route("/api/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = find_book(book_id)
    if book is None:
        return (
            jsonify({"success": False, "error": "Book not found"}),
            HTTPStatus.NOT_FOUND,
        )
    book_data = {"id": book.id, "title": book.title, "author": book.author, "year": book.year}
    return jsonify({"success": True, "data": book_data}), HTTPStatus.OK

@app.route("/api/books", methods=["POST"])
def create_book():
    if not request.is_json:
        return (
            jsonify({"success": False, "error": "Content-type must be application/json"}),
            HTTPStatus.BAD_REQUEST,
        )
    data = request.get_json()
    required_fields = ["title", "author", "year"]

    for field in required_fields:
        if field not in data:
            return (
                jsonify({"success": False, "error": f"Missing required field: {field}"}),
                HTTPStatus.BAD_REQUEST,
            )

    new_book = Book(title=data["title"], author=data["author"], year=data["year"])
    db.session.add(new_book)
    db.session.commit()

    return jsonify({"success": True, "data": {"id": new_book.id, "title": new_book.title, "author": new_book.author, "year": new_book.year}}), HTTPStatus.CREATED

@app.route("/api/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"success": False, "error": "Book not found"}), HTTPStatus.NOT_FOUND

    data = request.get_json()
    for key in ["title", "author", "year"]:
        if key in data:
            setattr(book, key, data[key])

    db.session.commit()

    updated_book = {"id": book.id, "title": book.title, "author": book.author, "year": book.year}
    return jsonify({"success": True, "data": updated_book}), HTTPStatus.OK


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = find_book(book_id)
    if book is None:
        return jsonify({"success": False, "error": "Book not found"}), HTTPStatus.NOT_FOUND

    db.session.delete(book)
    db.session.commit()
    return jsonify({"success": True, "message": "Book deleted successfully"}), HTTPStatus.OK

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Resource not found"}), HTTPStatus.NOT_FOUND


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"success": False, "error": "Internal Server Error"}), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == "__main__":
    app.run(debug=True)
