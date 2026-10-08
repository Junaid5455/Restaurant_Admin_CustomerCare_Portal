📅 Reservations & Table Management APIs
This document outlines the endpoints for managing tables and reservations.

Tables (Owner Only)
POST /api/v1/restaurants/tables/ - Create table (Auto-generates QR token)
{ "table_number": "1", "capacity": 4 }
GET /api/v1/restaurants/tables/ - List tables
PATCH/DELETE /api/v1/restaurants/tables/{id}/ - Update/Delete table
Reservations
Check Available Slots
GET /api/v1/restervations/available-slots/?restaurant_id=uuid&date=YYYY-MM-DD
Returns a list of hourly slots with availability status.

Create Reservation
POST /api/v1/reservations/ (Customer)

json

{
    "restaurant": "uuid",
    "reservation_time": "2026-10-10T18:00:00Z",
    "party_size": 4,
    "special_requests": "Birthday"
}
Confirm Reservation
POST /api/v1/reservations/{id}/confirm/ (Owner only)
Changes status from PENDING to CONFIRMED.

Cancel Reservation
POST /api/v1/reservations/{id}/cancel/ (Customer or Owner)
Changes status to CANCELLED.

text


---

### Run the Migrations and Tests!

1. Run migrations to create the new tables:
   ```bash
   python manage.py makemigrations restaurants
   python manage.py migrate
Run the tests:
bash

python manage.py test apps.restaurants.test_reservations