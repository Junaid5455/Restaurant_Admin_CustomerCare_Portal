📍 Order Tracking & History APIs
This document outlines the endpoints for tracking active orders and viewing order history.

Track Order Status
GET /api/v1/orders/{id}/track/

Returns the real-time status, estimated completion time, and items for a specific order. This endpoint is designed to be polled by the frontend every 10-30 seconds to update the customer.

Response:

{    "id": "uuid",    "order_number": "ORD-20260930-AB12",    "restaurant_name": "Test Pizza",    "order_type": "PICKUP",    "status": "PLACED",    "payment_status": "COMPLETED",    "placed_at": "2026-09-30T15:00:00Z",    "estimated_completion_time": "2026-09-30T15:20:00Z",    "items": [        {            "name": "Margherita",            "quantity": 1        }    ]}
Order History
GET /api/v1/orders/

Returns a paginated list of all past and active orders for the authenticated user.

Customers: See only their own orders (CART status is hidden).
Owners: See orders for their restaurant.
Staff: See orders for their assigned restaurant.