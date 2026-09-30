🛎️ Order Types & Selection APIs
Manage Saved Addresses
Customers can manage their delivery addresses via the Users API.

POST /api/v1/users/addresses/ - Save new addressGET /api/v1/users/addresses/ - List saved addressesPUT /api/v1/users/addresses/{id}/ - Update address

Order Checkout Flows
POST /api/v1/cart/checkout/

Depending on the order_type parameter, different fields are required:

1. Pickup Order Flow
{    "order_type": "PICKUP",    "pickup_time": "2026-10-01T18:00:00Z"}
No delivery fee is applied.

2. Delivery Order Flow
json

{
    "order_type": "DELIVERY",
    "address_id": "uuid-of-saved-address",
    "delivery_instructions": "Leave at the front door."
}
The API copies the address details to the order. A delivery fee is applied.

3. Dine-In Order Flow
json

{
    "order_type": "DINE_IN",
    "table_number": "12A",
    "number_of_guests": 4
}
