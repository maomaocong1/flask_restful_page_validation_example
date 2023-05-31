from flask import Flask, jsonify, request
from cerberus import Validator

app = Flask(__name__)

# Sample data
books = [
    {"id": 1, "title": "Python Crash Course", "author": "Eric Matthes"},
    {"id": 2, "title": "Fluent Python", "author": "Luciano Ramalho"},
    {"id": 3, "title": "Clean Code", "author": "Robert C. Martin"},
    # ...
]

# Validator schema for book validation
book_schema = {
    'id': {'type': 'integer', 'required': True, 'min': 1},
    'title': {'type': 'string', 'required': True},
    'author': {'type': 'string', 'required': True}
}

# Helper function for validating data against the schema
def validate_data(data, schema):
    validator = Validator(schema)
    if not validator.validate(data):
        return False, validator.errors
    return True, None

# GET request to retrieve paginated books with optional filtering
@app.route('/books', methods=['GET'])
def get_books():
    # Pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Filter parameters
    filter_title = request.args.get('title', None)
    filter_author = request.args.get('author', None)

    # Filter books based on title and author
    filtered_books = books
    if filter_title:
        filtered_books = [book for book in filtered_books if filter_title.lower() in book['title'].lower()]
    if filter_author:
        filtered_books = [book for book in filtered_books if filter_author.lower() in book['author'].lower()]

    # Calculate total pages and perform pagination
    total_books = len(filtered_books)
    total_pages = (total_books + per_page - 1) // per_page
    paginated_books = filtered_books[(page - 1) * per_page: page * per_page]

    return jsonify({
        'total_books': total_books,
        'total_pages': total_pages,
        'page': page,
        'per_page': per_page,
        'books': paginated_books
    })

# POST request to add a new book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    is_valid, errors = validate_data(data, book_schema)
    if not is_valid:
        return jsonify({'error': errors}), 400
    new_book = {
        'id': data['id'],
        'title': data['title'],
        'author': data['author']
    }
    books.append(new_book)
    return jsonify(new_book), 201

# PUT request to update an existing book
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    is_valid, errors = validate_data(data, book_schema)
    if not is_valid:
        return jsonify({'error': errors}), 400
    book = next((book for book in books if book['id'] == book_id), None)
    if book is None:
        return jsonify({'error': 'Book not found'}), 404
    book['title'] = data['title']
    book['author'] = data['author']
    return jsonify(book)

# DELETE request to remove a book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = next((book for book in books if book['id'] == book_id), None)
    if book is None:
        return jsonify({'error': 'Book not found'}), 404
    books.remove(book)
    return jsonify({'result': 'Book deleted'})

if __name__ == '__main__':
    app.run(debug=True)
