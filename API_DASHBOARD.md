📊 Restaurant Admin Dashboard APIs
This document outlines the endpoints for the restaurant owner's dashboard and analytics.

Dashboard Overview
GET /api/v1/analytics/dashboard/

Returns high-level KPIs for the owner's restaurant.

Response:

{    "restaurant_name": "Test Pizza",    "today_sales": "0.00",    "today_orders_count": 0,    "pending_orders": 0,    "completed_orders": 0,    "cancelled_orders": 0,    "total_sales": "32.00",    "total_orders": 2,    "total_customers": 1}
Popular Items
GET /api/v1/analytics/dashboard/popular_items/

Returns the top 5 most sold items for the restaurant.

Response:

json

[
    {
        "menu_item_id": "uuid",
        "name": "Margherita",
        "total_quantity_sold": 2,
        "total_revenue": "20.00"
    }
]
Recent Orders
GET /api/v1/analytics/dashboard/recent_orders/

Returns the 5 most recent orders placed at the restaurant.

Response:

json

[
    {
        "id": "uuid",
        "order_number": "ORD-...",
        "customer_email": "cust@test.com",
        "status": "PLACED",
        "total_amount": "10.00",
        "items_count": 1,
        "placed_at": "2026-10-07T..."
    }
]
text


---

### Run the Tests!

Run the following command to verify the dashboard logic:
```bash
python manage.py test apps.analytics.test_dashboard