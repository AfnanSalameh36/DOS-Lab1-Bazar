import sqlite3

import pytest
import requests

BOOK = {"title": "RPCs for Noobs", "quantity": 5, "price": 50}


class FakeResponse:
    """Minimal stand-in for a requests.Response."""

    def __init__(self, status_code, data=None):
        self.status_code = status_code
        self._data = data or {}

    def json(self):
        return self._data


def count_purchases():
    import database
    conn = sqlite3.connect(database.DATABASE_PATH)
    try:
        return conn.execute("SELECT COUNT(*) FROM purchases").fetchone()[0]
    finally:
        conn.close()


def test_health(order_app):
    resp = order_app.app.test_client().get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_purchase_success(order_app, monkeypatch):
    monkeypatch.setattr(order_app.requests, "get",
                        lambda *a, **k: FakeResponse(200, BOOK))
    monkeypatch.setattr(order_app.requests, "post",
                        lambda *a, **k: FakeResponse(200, {}))

    resp = order_app.app.test_client().post("/purchase/2")

    assert resp.status_code == 200
    assert resp.get_json() == {
        "status": "success",
        "message": "bought book RPCs for Noobs",
    }
    assert count_purchases() == 1


def test_purchase_book_not_found(order_app, monkeypatch):
    monkeypatch.setattr(order_app.requests, "get",
                        lambda *a, **k: FakeResponse(404, {}))

    def must_not_be_called(*a, **k):
        raise AssertionError("stock must not be updated for a missing book")
    monkeypatch.setattr(order_app.requests, "post", must_not_be_called)

    resp = order_app.app.test_client().post("/purchase/99")

    assert resp.status_code == 404
    assert count_purchases() == 0


def test_purchase_insufficient_stock(order_app, monkeypatch):
    monkeypatch.setattr(order_app.requests, "get",
                        lambda *a, **k: FakeResponse(200, BOOK))
    monkeypatch.setattr(order_app.requests, "post",
                        lambda *a, **k: FakeResponse(409, {}))

    resp = order_app.app.test_client().post("/purchase/2")

    assert resp.status_code == 409
    assert count_purchases() == 0


def test_catalog_unavailable(order_app, monkeypatch):
    def down(*a, **k):
        raise requests.ConnectionError("catalog is down")
    monkeypatch.setattr(order_app.requests, "get", down)

    resp = order_app.app.test_client().post("/purchase/2")

    assert resp.status_code == 503
    assert count_purchases() == 0


def test_stock_restored_if_saving_fails(order_app, monkeypatch):
    posts = []
    monkeypatch.setattr(order_app.requests, "get",
                        lambda *a, **k: FakeResponse(200, BOOK))

    def fake_post(url, json=None, **k):
        posts.append(json)
        return FakeResponse(200, {})
    monkeypatch.setattr(order_app.requests, "post", fake_post)

    def boom(*a, **k):
        raise RuntimeError("disk error")
    monkeypatch.setattr(order_app, "save_purchase", boom)

    resp = order_app.app.test_client().post("/purchase/2")

    assert resp.status_code == 500
    # first decrement, then the undo (+1)
    assert posts == [{"quantity_delta": -1}, {"quantity_delta": 1}]