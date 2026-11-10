import requests


class FakeResponse:
    """Minimal stand-in for a requests.Response."""

    def __init__(self, status_code, data=None, bad_json=False):
        self.status_code = status_code
        self._data = data
        self._bad_json = bad_json

    def json(self):
        if self._bad_json:
            raise ValueError("not json")
        return self._data


def record_calls(monkeypatch, frontend_app, response):
    """Replace requests.request; return the list of calls it receives."""
    calls = []

    def fake_request(method, url, **kwargs):
        calls.append((method, url))
        return response

    monkeypatch.setattr(frontend_app.requests, "request", fake_request)
    return calls


def test_health(frontend_app):
    resp = frontend_app.app.test_client().get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"service": "frontend", "status": "ok"}


def test_search_forwards_to_catalog(frontend_app, monkeypatch):
    books = [{"id": 1, "title": "How to get a good grade in DOS"}]
    calls = record_calls(monkeypatch, frontend_app, FakeResponse(200, books))

    resp = frontend_app.app.test_client().get("/search/distributed%20systems")

    assert resp.status_code == 200
    assert resp.get_json() == books
    # the space in the topic must stay URL-encoded
    assert calls == [
        ("GET", f"{frontend_app.CATALOG_URL}/search/distributed%20systems")
    ]


def test_info_forwards_to_catalog(frontend_app, monkeypatch):
    book = {"title": "RPCs for Noobs", "quantity": 5, "price": 50}
    calls = record_calls(monkeypatch, frontend_app, FakeResponse(200, book))

    resp = frontend_app.app.test_client().get("/info/2")

    assert resp.status_code == 200
    assert resp.get_json() == book
    assert calls == [("GET", f"{frontend_app.CATALOG_URL}/info/2")]


def test_purchase_forwards_to_order(frontend_app, monkeypatch):
    reply = {"status": "success", "message": "bought book RPCs for Noobs"}
    calls = record_calls(monkeypatch, frontend_app, FakeResponse(200, reply))

    resp = frontend_app.app.test_client().post("/purchase/2")

    assert resp.status_code == 200
    assert resp.get_json() == reply
    assert calls == [("POST", f"{frontend_app.ORDER_URL}/purchase/2")]


def test_backend_error_status_is_passed_through(frontend_app, monkeypatch):
    record_calls(monkeypatch, frontend_app,
                 FakeResponse(409, {"error": "Insufficient stock"}))

    resp = frontend_app.app.test_client().post("/purchase/2")

    assert resp.status_code == 409
    assert resp.get_json() == {"error": "Insufficient stock"}


def test_backend_down_returns_503(frontend_app, monkeypatch):
    def down(*args, **kwargs):
        raise requests.ConnectionError("backend is down")

    monkeypatch.setattr(frontend_app.requests, "request", down)

    resp = frontend_app.app.test_client().get("/info/1")

    assert resp.status_code == 503
    assert "error" in resp.get_json()


def test_invalid_backend_reply_returns_502(frontend_app, monkeypatch):
    record_calls(monkeypatch, frontend_app,
                 FakeResponse(200, bad_json=True))

    resp = frontend_app.app.test_client().get("/info/1")

    assert resp.status_code == 502


def test_info_rejects_non_integer_id(frontend_app):
    resp = frontend_app.app.test_client().get("/info/abc")
    assert resp.status_code == 404