📈 Analytics & Reports APIs
This document outlines the endpoints for generating business reports and analytics.

Sales Report
GET /api/v1/analytics/dashboard/sales-report/?period=daily

Returns aggregated sales data grouped by day or month.Query Parameters:

period: daily (last 30 days), weekly (last 7 days), or monthly (last 12 months).
Response:

[    {        "date": "2026-10-08",        "total_orders": 5,        "total_sales": "75.00",        "average_order_value": "15.00"    }]
Customer Analytics
GET /api/v1/analytics/dashboard/customer-analytics/
Returns the top 10 customers by total spend.

Operational Metrics
GET /api/v1/analytics/dashboard/operational-metrics/
Returns the top 5 peak business hours based on order volume.

Export Sales Report (CSV)
GET /api/v1/analytics/dashboard/export-sales/
Triggers a download of a CSV file containing the last 30 days of orders.

text


---

### Run the Tests!

Run the following command to verify the reporting logic:
```bash
python manage.py test apps.analytics.test_report