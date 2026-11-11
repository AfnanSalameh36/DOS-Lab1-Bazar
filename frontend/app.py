import os
from urllib.parse import quote

import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Service addresses: can be overridden later (e.g. Docker) without touching code
CATALOG_URL = os.environ.get("CATALOG_URL", "http://127.0.0.1:5001")
ORDER_URL = os.environ.get("ORDER_URL", "http://127.0.0.1:5002")


def forward(method, url):
    """Send the request to a backend service and return its reply as is."""
    try:
        resp = requests.request(method, url, timeout=5)
    except requests.RequestException:
        return jsonify({"error": "Backend service unavailable"}), 503

    try:
        body = resp.json()
    except ValueError:
        return jsonify({"error": "Invalid reply from backend"}), 502

    return jsonify(body), resp.status_code


@app.get("/health")
def health():
    return jsonify({"service": "frontend", "status": "ok"}), 200


@app.get("/search/<topic>")
def search(topic):
    print(f"search: {topic}", flush=True)
    return forward("GET", f"{CATALOG_URL}/search/{quote(topic)}")


@app.get("/info/<int:item_id>")
def info(item_id):
    print(f"info: {item_id}", flush=True)
    return forward("GET", f"{CATALOG_URL}/info/{item_id}")


@app.post("/purchase/<int:item_id>")
def purchase(item_id):
    print(f"purchase: {item_id}", flush=True)
    return forward("POST", f"{ORDER_URL}/purchase/{item_id}")


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    app.run(host=host, port=5000, debug=False)