📣 Marketing & Notifications APIs
This document outlines the endpoints for managing marketing campaigns and user notifications.

Campaigns (Owner Only)
POST /api/v1/users/campaigns/ - Create campaign (Requires restaurant_id)
{    "restaurant_id": "uuid",    "name": "Summer Sale",    "channel": "EMAIL",     "target_segment": "ALL",     "subject": "20% Off!",    "body": "Get 20% off your next order."}
GET /api/v1/users/campaigns/ - List campaigns
POST /api/v1/users/campaigns/{id}/send/ - Trigger the campaign (Filters by preferences and segment)
Notification Preferences (Customer)
GET /api/v1/users/preferences/ - Get preferences
POST /api/v1/users/preferences/ - Create preferences (if not exists)
PATCH /api/v1/users/preferences/{id}/ - Update opt-in status
json

{ "email_promotions": true, "sms_promotions": false, "push_promotions": true }
Notifications (Customer)
GET /api/v1/users/notifications/ - List user notifications
POST /api/v1/users/notifications/{id}/mark-read/ - Mark as read
text


---

### Run the Migrations and Tests!

1. Run migrations to create the new tables:
   ```bash
   python manage.py makemigrations users
   python manage.py migrate
Run the tests:
bash

python manage.py test apps.users.test_marketing