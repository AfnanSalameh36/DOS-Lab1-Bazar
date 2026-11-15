import os
import requests
from flask import Flask, jsonify
from database import init_db, save_purchase

app = Flask(__name__)

# Catalog address: can be changed later (e.g. Docker) without touching code
CATALOG_URL = os.environ.get("CATALOG_URL", "http://127.0.0.1:5001")

# Create the purchases table if needed
init_db()


@app.get("/health")
def health():
    return jsonify({"service": "order", "status": "ok"}), 200


@app.post("/purchase/<int:item_id>")
def purchase(item_id):
    # Step 1: ask Catalog if the book exists
    try:
        info = requests.get(f"{CATALOG_URL}/info/{item_id}", timeout=5)
    except requests.RequestException:
        return jsonify({"error": "Catalog service unavailable"}), 503

    if info.status_code == 404:
        return jsonify({"error": "Book not found"}), 404
    if info.status_code != 200:
        return jsonify({"error": "Catalog service error"}), 503

    title = info.json()["title"]

    # Step 2: ask Catalog to decrement stock by 1 (atomic on its side)
    try:
        update = requests.post(
            f"{CATALOG_URL}/update/{item_id}",
            json={"quantity_delta": -1},
            timeout=5,
        )
    except requests.RequestException:
        return jsonify({"error": "Catalog service unavailable"}), 503

    if update.status_code == 409:
        return jsonify({"error": "Insufficient stock"}), 409
    if update.status_code == 404:
        return jsonify({"error": "Book not found"}), 404
    if update.status_code != 200:
        return jsonify({"error": "Catalog service error"}), 503

    # Step 3: save the purchase, only after the stock was decremented
    try:
        save_purchase(item_id, title)
    except Exception:
        # Undo the stock decrement so the books are not lost
        try:
            requests.post(f"{CATALOG_URL}/update/{item_id}",
                          json={"quantity_delta": 1}, timeout=5)
        except requests.RequestException:
            pass
        return jsonify({"error": "Could not record purchase"}), 500

    print(f"bought book {title}", flush=True)
    return jsonify({
        "status": "success",
        "message": f"bought book {title}"
    }), 200


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    app.run(host=host, port=5002, debug=False)