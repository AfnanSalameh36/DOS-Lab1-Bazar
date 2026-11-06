# Bazar.com - API Contract (v1)

## General
- Three services: Front-end, Catalog, Order.
- Communication: HTTP REST.
- Responses: JSON.
- Book IDs are integers.

## Front-end API
- GET /search/<topic> -> Forward request to Catalog.
- GET /info/<id> -> Forward request to Catalog.
- POST /purchase/<id> -> Forward request to Order.

## Catalog API
- GET /search/<topic>
  Response: [{"id": 1, "title": "How to get a good grade in DOS in 40 minutes a day"}]

- GET /info/<id>
  Response: {"title": "RPCs for Noobs", "quantity": 5, "price": 50}

- POST /update/<id>
  Request: {"quantity_delta": -1} OR {"price": 55}
  Response: Updated book information.
  Quantity updates must be atomic and cannot reduce stock below zero.

## Order API
- POST /purchase/<id>
  On success: {"status": "success", "message": "bought book RPCs for Noobs"}
  On failure: Return a JSON error without recording a successful purchase.

## Error Handling
- 400: Invalid request data.
- 404: Book not found.
- 409: Insufficient stock.
- 503: Required service unavailable.

## Purchase Flow
1. Order queries Catalog for book information.
2. Catalog confirms whether the book exists.
3. Order requests an atomic stock decrement from Catalog.
4. If stock is unavailable, return failure.
5. If decrement succeeds, Order saves the purchase to persistent storage.
6. Order returns success to Front-end.

## Shared Rules
- Services do not directly access each other's databases.
- Catalog owns book inventory.
- Order owns the purchase log.
- All services must support concurrent HTTP requests.
- Both partners can use mock responses during independent development.
