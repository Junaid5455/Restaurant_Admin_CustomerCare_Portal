🍳 Kitchen Display System (KDS) APIs
This document outlines the endpoints used by the kitchen display screen.

List Active Kitchen Orders
GET /api/v1/kitchen/orders/

Returns orders that are currently CONFIRMED or PREPARING.

Prices are omitted.
Items include customizations and add-ons clearly formatted.
Sorted by oldest first.
Response:

[    {        "id": "uuid",        "order_number": "ORD-...",        "order_type": "DINE_IN",        "table_number": "12A",        "status": "PREPARING",        "placed_at": "...",        "confirmed_at": "...",        "items": [            {                "id": "uuid",                "item_name": "Margherita",                "quantity": 1,                "special_instructions": null,                "customizations": [],                "add_ons": []            }        ]    }]
Start Preparation
POST /api/v1/kitchen/orders/{id}/start/

Changes order status from CONFIRMED to PREPARING.

Mark Ready
POST /api/v1/kitchen/orders/{id}/ready/

Changes order status from PREPARING to READY. This triggers the frontend to notify the customer that their food is ready for pickup/delivery.

text


---

### Run the Tests!

Run the following command to verify the KDS logic:
```bash
python manage.py test apps.kitchen.test_kds