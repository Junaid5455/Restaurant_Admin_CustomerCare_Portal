This document outlines the endpoints for browsing menu categories, items, filtering, and recommendations.

Menu Categories
List Categories
GET /api/v1/menu/categories/

Query Parameters:

restaurant_id: Filter by restaurant (e.g., ?restaurant_id=uuid)
search: Search by category name
Get Category Details
GET /api/v1/menu/categories/{id}/Returns category details along with nested active items.

Get Items in Category
GET /api/v1/menu/categories/{id}/items/Returns a paginated list of available items in the specific category.

Menu Items
List Menu Items
GET /api/v1/menu/items/

Query Parameters:

search: Search by item name or description
restaurant_id: Filter by restaurant
category_id: Filter by category
is_vegetarian: True or False
is_vegan: True or False
is_spicy: True or False
is_featured: True (Filter for deals/featured items)
is_new: True (Filter for new arrivals)
min_price / max_price: Filter by price range
ordering: Sort by name, price, rating, preparation_time_minutes
Get Menu Item Details
GET /api/v1/menu/items/{id}/

Returns full item details including nested customizations (with options) and add_ons.

Special Item Collections
Featured Items (Deals)
GET /api/v1/menu/items/featured/Returns top 10 items marked as is_featured.

New Arrivals
GET /api/v1/menu/items/new_arrivals/Returns top 10 items marked as is_new.

Recommended Items
GET /api/v1/menu/items/recommended/Returns top 10 recommended items based on high rating (>= 4.0) or featured status.

