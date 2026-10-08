🛵 Delivery Management APIs
This document outlines the endpoints for managing deliveries, assigning drivers, and real-time tracking.

List Deliveries
GET /api/v1/delivery/

Owners: See deliveries for their restaurant.
Drivers: See only deliveries assigned to them.
Customers: See their own deliveries.
Assign Driver
POST /api/v1/delivery/{id}/assign-driver/(Owner only) Assigns a driver to a delivery. Changes status from PENDING to ASSIGNED.

Body:

{    "driver_id": "uuid-of-restaurant-staff-member"}
Update Location (Real-time tracking)
POST /api/v1/delivery/{id}/update-location/
(Driver only) Updates the driver's current GPS coordinates.

Body:

json

{
    "latitude": "40.712776",
    "longitude": "-74.005974"
}
Mark Picked Up
POST /api/v1/delivery/{id}/mark-picked-up/
(Driver only) Indicates the driver has picked up the food from the restaurant.

Updates Delivery status to PICKED_UP.
Updates Order status to OUT_FOR_DELIVERY.
Mark Delivered
POST /api/v1/delivery/{id}/mark-delivered/
(Driver only) Indicates the food has been delivered to the customer.

Updates Delivery status to DELIVERED.
Updates Order status to DELIVERED.
text


---

### Run the Tests!

Run the following command to verify the delivery management logic:
```bash
python manage.py test apps.delivery.test_deliverie