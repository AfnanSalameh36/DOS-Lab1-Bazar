import requests

BASE_URL = "http://127.0.0.1:5000"


def search(topic):
    response = requests.get(f"{BASE_URL}/search/{topic}")
    response.raise_for_status()

    print("\n========== SEARCH RESULTS ==========")
    for book in response.json():
        print(f"ID: {book['id']} | Title: {book['title']}")


def info(item_id):
    response = requests.get(f"{BASE_URL}/info/{item_id}")
    response.raise_for_status()

    book = response.json()

    print("\n========== BOOK INFORMATION ==========")
    print(f"Title: {book['title']}")
    print(f"Price: {book['price']}")
    print(f"Quantity: {book['quantity']}")


def purchase(item_id):
    response = requests.post(f"{BASE_URL}/purchase/{item_id}")

    print("\n========== PURCHASE RESULT ==========")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")


if __name__ == "__main__":
    print("Welcome to Bazar.com")

    search("distributed systems")
    info(2)
    purchase(2)
    info(2)