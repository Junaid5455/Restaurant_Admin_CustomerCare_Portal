👥 Staff Management APIs
This document outlines the endpoints for restaurant owners to manage their staff.

List/View Staff
GET /api/v1/restaurants/staff/Returns all staff members for the owner's restaurant.

Add Staff Member
POST /api/v1/restaurants/staff/

If the provided staff_email belongs to an existing customer, their role is upgraded to RESTAURANT_STAFF. If the email doesn't exist, a new user account is created.

Body:

{    "staff_email": "newemployee@test.com",    "role": "KITCHEN_STAFF",    "can_manage_orders": true,    "can_view_analytics": false}
(Valid Roles: ADMIN, MANAGER, CASHIER, KITCHEN_STAFF, DELIVERY_STAFF, STOCK_STAFF)

Update Staff Details
PATCH /api/v1/restaurants/staff/{id}/
Update role or other base fields.

Toggle Active Status
POST /api/v1/restaurants/staff/{id}/toggle-active/
Activates or deactivates the staff member. Deactivated staff cannot log in to the admin panel.

Update Permissions
POST /api/v1/restaurants/staff/{id}/update-permissions/
Granularly update what the staff member is allowed to do.

Body:

json

{
    "can_manage_menu": true,
    "can_manage_orders": true,
    "can_manage_staff": false,
    "can_manage_payments": true,
    "can_view_analytics": true
}
text


---

### Run the Tests!

Run the following command to verify the staff management logic:
```bash
python manage.py test apps.restaurants.test_staff