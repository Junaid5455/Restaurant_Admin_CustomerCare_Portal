💳 Payment Processing APIs
This document outlines the endpoints for processing payments, handling Cash on Delivery (COD), confirming card payments, and processing refunds.

Process Payment
POST /api/v1/payments/process/

Initiates a payment for an order. If a card method is selected, it returns a Stripe client_secret for the frontend. If COD is selected, it confirms the order immediately.

Body:

{    "order_id": "uuid-of-order",    "payment_method": "CREDIT_CARD" }
(Valid methods: CREDIT_CARD, DEBIT_CARD, STRIPE, CASH_ON_DELIVERY, CASH_AT_RESTAURANT)

Response (Card):

json

{
    "payment": { "id": "uuid", "status": "PENDING", ... },
    "client_secret": "stripe_secret_key_for_frontend"
}
Confirm Payment
POST /api/v1/payments/confirm/

Verifies the payment status with the gateway (Stripe) and marks the order as paid and confirmed.

Body:

json

{
    "payment_id": "uuid-of-payment"
}
Process Refund
POST /api/v1/payments/{payment_id}/refund/

Refunds a completed payment. Only the order owner or Super Admin can process refunds.

Body:

json

{
    "amount": "10.50"
}
Get Payment Details / Receipt
GET /api/v1/payments/{payment_id}/

Returns the details of a specific payment transaction.

Saved Payment Methods
List Saved Cards
GET /api/v1/payments/methods/

Save a Card
POST /api/v1/payments/methods/

json

{
    "payment_method_type": "CREDIT_CARD",
    "is_default": true,
    "card_last_four": "4242",
    "card_brand": "Visa",
    "card_expiry_month": 12,
    "card_expiry_year": 2027,
    "token": "stripe_setup_intent_token"
}
Delete a Card
DELETE /api/v1/payments/methods/{id}/

text


---

### Run the Tests!

Run the following command to verify the payment flows:
```bash
python manage.py test apps.payments.test_payments