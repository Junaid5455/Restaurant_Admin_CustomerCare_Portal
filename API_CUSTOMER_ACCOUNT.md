👤 Customer Account Management APIs
This document outlines the endpoints for managing customer accounts, favorites, rewards, and gift cards.

Profile
GET /api/v1/auth/me/ - View profile
PUT /api/v1/auth/me/ - Update profile
Saved Addresses
GET /api/v1/users/addresses/ - List addresses
POST /api/v1/users/addresses/ - Save new address
DELETE /api/v1/users/addresses/{id}/ - Delete address
Saved Payment Methods
GET /api/v1/payments/methods/ - List saved cards
POST /api/v1/payments/methods/ - Save new card
DELETE /api/v1/payments/methods/{id}/ - Delete card
Favorites
Restaurants
GET /api/v1/users/favorites/restaurants/ - List favorite restaurants
POST /api/v1/users/favorites/restaurants/
{ "restaurant_id": "uuid" }
DELETE /api/v1/users/favorites/restaurants/{id}/ - Remove favorite
Menu Items
GET /api/v1/users/favorites/items/ - List favorite items
POST /api/v1/users/favorites/items/
json

{ "menu_item_id": "uuid" }
DELETE /api/v1/users/favorites/items/{id}/ - Remove favorite
Rewards & Gift Cards
GET /api/v1/users/rewards/ - View loyalty points, total orders, and total spent
GET /api/v1/users/gift-cards/ - View active gift cards and balances