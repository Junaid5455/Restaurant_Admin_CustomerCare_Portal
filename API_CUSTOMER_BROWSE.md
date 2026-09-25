🛒 Customer API - Browse Restaurants
This document outlines the read-only endpoints for customers to browse restaurants and menus.

Restaurants
List Restaurants
GET /api/v1/restaurants/

Query Parameters:

search: Search by name, city, etc. (e.g., ?search=pizza)
is_featured: Filter featured (e.g., ?is_featured=true)
allows_delivery: Filter by delivery (e.g., ?allows_delivery=true)
ordering: Sort order (e.g., ?ordering=-rating)
Get Restaurant Details
GET /api/v1/restaurants/{id}/

Get Restaurant Menu
GET /api/v1/restaurants/{id}/menu/Returns categories with nested active menu items.

Search Restaurants
GET /api/v1/restaurants/search/?q={query}Requires a query string of at least 2 characters.

Menu
List Menu Categories
GET /api/v1/menu/categories/

restaurant_id: Filter by restaurant (e.g., ?restaurant_id=uuid)
Get Items in Category
GET /api/v1/menu/categories/{id}/items/

List Menu Items
GET /api/v1/menu/items/Query Parameters:

search: Search by item name
restaurant_id: Filter by restaurant
category_id: Filter by category
is_vegetarian: true or false
min_price / max_price: Filter by price range
Get Menu Item Details
GET /api/v1/menu/items/{id}/Includes nested customizations, options, and add-ons.

Get Featured Items
GET /api/v1/menu/items/featured/Returns top 10 featured items across all active restaurants.