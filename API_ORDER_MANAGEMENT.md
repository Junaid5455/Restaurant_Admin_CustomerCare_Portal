📦 Order Management APIs (Admin)
This document outlines the endpoints for restaurant owners and staff to manage orders.

List/Filter Orders
GET /api/v1/orders/

Returns orders based on the user's role. Owners see their restaurant's orders, staff see their assigned restaurant's orders.

Query Parameters:

status: Filter by status (e.g., ?status=PLACED, ?status=PREPARING)
order_type: Filter by type (e.g., ?order_type=PICKUP)
payment_status: Filter by payment (e.g., ?payment_status=PENDING)
Get Order Details
GET /api/v1/orders/{id}/

Returns full details of a specific order, including items, customizations, and totals.

Update Order Status
POST /api/v1/orders/{id}/update-status/

Updates the status of an order (e.g., confirming it, marking it as preparing).

Body:

{    "status": "CONFIRMED"}
(Valid statuses: PLACED, CONFIRMED, PREPARING, READY, OUT_FOR_DELIVERY, DELIVERED)

Cancel Order
POST /api/v1/orders/{id}/cancel/

Cancels an order. Can only be done if the order is currently PLACED or CONFIRMED.

Body (Optional):

json

{
    "reason": "Customer changed their mind"
}
text


---

### Run the Tests!

Run the following command to verify the order management logic:
```bash
python manage.py test apps.orders.test_management