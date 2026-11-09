
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import requests

BASE = "http://127.0.0.1:5001"
BOOK_ID = 2

info_url = f"{BASE}/info/{BOOK_ID}"
update_url = f"{BASE}/update/{BOOK_ID}"

# Remember the original stock
original = requests.get(info_url, timeout=10).json()["quantity"]

# Synchronize the two requests
barrier = Barrier(2)


def decrease_stock():
    barrier.wait()
    response = requests.post(
        update_url,
        json={"quantity_delta": -1},
        timeout=10
    )
    return response.status_code


try:
    # Prepare exactly one available copy
    response = requests.post(
        update_url,
        json={"quantity_delta": 1 - original},
        timeout=10
    )
    response.raise_for_status()

    # Send two concurrent requests
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(
            lambda _: decrease_stock(), range(2)
        ))

    remaining = requests.get(
        info_url, timeout=10
    ).json()["quantity"]

    print("HTTP responses:", results)
    print("Remaining quantity:", remaining)

    assert sorted(results) == [200, 409]
    assert remaining == 0

    print("Concurrency test PASSED!")

finally:
    # Restore the original stock
    current = requests.get(
        info_url, timeout=10
    ).json()["quantity"]

    response = requests.post(
        update_url,
        json={"quantity_delta": original - current},
        timeout=10
    )
    response.raise_for_status()

    print("Original stock restored.")
