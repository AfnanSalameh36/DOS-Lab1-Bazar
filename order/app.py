
from flask import Flask, jsonify

# Create the Order Service application
app = Flask(__name__)


# Health check endpoint
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "Order Service",
        "status": "running"
    }), 200


# Run the server
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)
