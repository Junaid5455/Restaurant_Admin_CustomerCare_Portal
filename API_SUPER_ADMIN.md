🛡️ Super Admin Panel APIs
This document outlines the endpoints for the platform Super Admin.

Dashboard Overview
GET /api/v1/admin/dashboard/Returns high-level KPIs for the entire platform.

total_revenue (from delivered orders)
total_orders
active_restaurants
total_customers
open_support_tickets
User Management
GET /api/v1/admin/users/List all users on the platform.

POST /api/v1/admin/users/{id}/toggle-user-active/Blocks or unblocks a user account. Blocked users cannot log in.

Restaurant Management
GET /api/v1/admin/restaurants/List all restaurants on the platform.

POST /api/v1/admin/restaurants/{id}/toggle-restaurant-active/Activates or deactivates a restaurant. Deactivated restaurants are hidden from customers.

Order Management
GET /api/v1/admin/orders/View the last 50 platform-wide orders.

Run the Tests!
Run the following command to verify the Super Admin logic:

bash

python manage.py test apps.common.test_admin