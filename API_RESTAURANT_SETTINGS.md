⚙️ Restaurant Settings Management APIs
This document outlines the endpoints for restaurant owners to manage their profile, operating hours, holidays, and delivery zones.

Profile & Operations Settings
GET /api/v1/restaurants/settings/PATCH /api/v1/restaurants/settings/

Get or update the restaurant's details, operating hours, fees, and tax rate. The API automatically knows which restaurant to update based on the logged-in owner's token.

PATCH Body (Partial Updates allowed):

{    "name": "Updated Name",    "opening_time": "08:00:00",    "delivery_fee": "4.50",    "tax_rate": "8.00"}
Holidays / Closures
GET /api/v1/restaurants/holidays/ - List holidays
POST /api/v1/restaurants/holidays/ - Add holiday
json

{ "holiday_date": "2026-12-25", "reason": "Christmas" }
DELETE /api/v1/restaurants/holidays/{id}/ - Remove holiday
Delivery Zones
GET /api/v1/restaurants/delivery-zones/ - List delivery zones
POST /api/v1/restaurants/delivery-zones/ - Add delivery zone
json

{
    "zone_name": "Downtown",
    "delivery_fee": "4.00",
    "delivery_time_minutes": 45,
    "postal_codes": "10001,10002",
    "is_active": true
}
PUT/PATCH /api/v1/restaurants/delivery-zones/{id}/ - Update zone
DELETE /api/v1/restaurants/delivery-zones/{id}/ - Delete zone
text


---

### Run the Tests!

Run the following command to verify the settings logic:
```bash
python manage.py test apps.restaurants.test_settings