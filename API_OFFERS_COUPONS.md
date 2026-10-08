🎟️ Offers & Coupons Management APIs
This document outlines the endpoints for restaurant owners to manage coupons and promotional offers.

Create Coupon
POST /api/v1/coupons/

Creates a new coupon code for a specific restaurant.

Body:

{    "restaurant_id": "uuid-of-restaurant",    "code": "SUMMER5",     "description": "$5 off any order over $25",    "discount_type": "FIXED",     "discount_value": "5.00",    "min_order_amount": "25.00",    "max_uses": 100,    "valid_from": "2026-10-08T12:00:00Z",    "valid_to": "2026-11-08T12:00:00Z"}
(Valid Discount Types: PERCENTAGE, FIXED)

List Coupons
GET /api/v1/coupons/
Returns all coupons for the owner's restaurants. Includes times_used and nested redemptions array so owners can see who used them.

Update Coupon
PATCH /api/v1/coupons/{id}/
Update valid dates, max uses, or discount values.

Toggle Active Status
POST /api/v1/coupons/{id}/toggle-active/
Quickly activates or deactivates a coupon. Deactivated coupons cannot be applied to new orders.

text


---

### Run the Migrations and Tests!

1. Run migrations to create the new tables:
   ```bash
   python manage.py makemigrations orders
   python manage.py migrate
Run the tests:
bash

python manage.py test apps.orders.test_coupons