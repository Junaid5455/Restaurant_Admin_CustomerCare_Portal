🎫 Customer Support System APIs
This document outlines the endpoints for creating support tickets, chatting with support staff, and closing tickets.

Create Support Ticket
POST /api/v1/support/tickets/

Allows a customer to report an issue (e.g., missing items, refund request).

Body:

{    "restaurant": "uuid-of-restaurant",    "related_order": "uuid-of-order",    "subject": "Missing item",    "description": "I didn't receive my drink",    "category": "MISSING_ITEMS",     "priority": "HIGH"}
(Valid Categories: ORDER_ISSUE, DELIVERY_ISSUE, PAYMENT_ISSUE, MISSING_ITEMS, INCORRECT_ITEMS, QUALITY_ISSUE, REFUND_REQUEST, GENERAL_INQUIRY, OTHER)

List/View Tickets
GET /api/v1/support/tickets/

Returns tickets. Customers see their own; Owners see tickets for their restaurant.

Add Message to Ticket
POST /api/v1/support/tickets/{id}/add_message/

Sends a message in the support chat. Automatically sets the message_type based on who is logged in.

Body:

json

{
    "message": "Hello, I need a refund."
}
Close Ticket
POST /api/v1/support/tickets/{id}/close/

Closes the ticket. Can be done by the customer or staff.

text


---

### Run the Tests!

Run the following command to verify the support system:
```bash
python manage.py test apps.support.test_tickets