"""
Application-wide constants for the Restaurant Portal.
"""

# ====================================================
# User Roles
# ====================================================
class UserRoles:
    CUSTOMER = "customer"
    RESTAURANT_OWNER = "restaurant_owner"
    RESTAURANT_STAFF = "restaurant_staff"
    KITCHEN_STAFF = "kitchen_staff"
    DELIVERY_STAFF = "delivery_staff"
    SUPPORT_AGENT = "support_agent"
    SUPER_ADMIN = "super_admin"

    CHOICES = [
        (CUSTOMER, "Customer"),
        (RESTAURANT_OWNER, "Restaurant Owner"),
        (RESTAURANT_STAFF, "Restaurant Staff"),
        (KITCHEN_STAFF, "Kitchen Staff"),
        (DELIVERY_STAFF, "Delivery Staff"),
        (SUPPORT_AGENT, "Support Agent"),
        (SUPER_ADMIN, "Super Admin"),
    ]


# ====================================================
# Order Status
# ====================================================
class OrderStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

    CHOICES = [
        (PENDING, "Pending"),
        (CONFIRMED, "Confirmed"),
        (PREPARING, "Preparing"),
        (READY, "Ready"),
        (OUT_FOR_DELIVERY, "Out for Delivery"),
        (DELIVERED, "Delivered"),
        (CANCELLED, "Cancelled"),
        (REFUNDED, "Refunded"),
    ]


# ====================================================
# Payment Status
# ====================================================
class PaymentStatus:
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

    CHOICES = [
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
        (REFUNDED, "Refunded"),
    ]


# ====================================================
# Payment Methods
# ====================================================
class PaymentMethods:
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    CASH = "cash"
    WALLET = "wallet"
    STRIPE = "stripe"

    CHOICES = [
        (CREDIT_CARD, "Credit Card"),
        (DEBIT_CARD, "Debit Card"),
        (CASH, "Cash on Delivery"),
        (WALLET, "Wallet"),
        (STRIPE, "Stripe"),
    ]


# ====================================================
# Order Types
# ====================================================
class OrderTypes:
    DINE_IN = "dine_in"
    TAKEAWAY = "takeaway"
    DELIVERY = "delivery"

    CHOICES = [
        (DINE_IN, "Dine In"),
        (TAKEAWAY, "Takeaway"),
        (DELIVERY, "Delivery"),
    ]


# ====================================================
# Pagination Defaults
# ====================================================
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# ====================================================
# API Configuration
# ====================================================
API_VERSION = "v1"
API_PREFIX = "api"