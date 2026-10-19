"""Small, reproducible synthetic warehouse fixture."""
ORDERS = [
    {"order_id": "o1", "customer_id": "c1", "region": "East", "ordered_on": "2026-01-05", "amount": 120.0, "refund": 0.0},
    {"order_id": "o2", "customer_id": "c2", "region": "West", "ordered_on": "2026-01-11", "amount": 80.0, "refund": 20.0},
    {"order_id": "o3", "customer_id": "c1", "region": "East", "ordered_on": "2026-02-02", "amount": 150.0, "refund": 0.0},
    {"order_id": "o4", "customer_id": "c3", "region": "West", "ordered_on": "2026-02-19", "amount": 50.0, "refund": 50.0},
    {"order_id": "o5", "customer_id": "c4", "region": "North", "ordered_on": "2026-03-03", "amount": 200.0, "refund": 0.0},
    {"order_id": "o6", "customer_id": "c2", "region": "West", "ordered_on": "2026-03-21", "amount": 100.0, "refund": 10.0},
]

ORDER_ITEMS = [
    {"item_id": "i1", "order_id": "o1", "quantity": 1},
    {"item_id": "i2", "order_id": "o1", "quantity": 2},
    {"item_id": "i3", "order_id": "o2", "quantity": 1},
    {"item_id": "i4", "order_id": "o3", "quantity": 3},
    {"item_id": "i5", "order_id": "o4", "quantity": 1},
    {"item_id": "i6", "order_id": "o5", "quantity": 2},
    {"item_id": "i7", "order_id": "o6", "quantity": 1},
]
