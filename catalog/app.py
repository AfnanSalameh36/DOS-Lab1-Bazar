
import math
from flask import Flask, jsonify, request
from database import init_db, search_books, get_book, update_book

app = Flask(__name__)

# Create database and initial books if needed
init_db()


@app.get("/search/<topic>")
def search(topic):
    return jsonify(search_books(topic.strip()))


@app.get("/info/<int:item_id>")
def info(item_id):
    book = get_book(item_id)

    if book is None:
        return jsonify({"error": "Book not found"}), 404

    return jsonify(book)


@app.post("/update/<int:item_id>")
def update(item_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "JSON object required"}), 400

    has_delta = "quantity_delta" in data
    has_price = "price" in data

    if has_delta == has_price or len(data) != 1:
        return jsonify({
            "error": "Send either quantity_delta or price"
        }), 400

    if has_delta:
        delta = data["quantity_delta"]

        if type(delta) is not int:
            return jsonify({
                "error": "quantity_delta must be an integer"
            }), 400

        status, book = update_book(
            item_id, quantity_delta=delta
        )

    else:
        price = data["price"]

        if (type(price) not in (int, float)
                or not math.isfinite(price)
                or price < 0):
            return jsonify({
                "error": "Price must be a non-negative number"
            }), 400

        status, book = update_book(item_id, price=price)

    if status == "not_found":
        return jsonify({"error": "Book not found"}), 404

    if status == "insufficient_stock":
        return jsonify({"error": "Insufficient stock"}), 409

    return jsonify(book), 200


if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5001, debug=False)
