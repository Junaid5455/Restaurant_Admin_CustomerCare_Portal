from django.contrib import admin
from .models import DailySalesReport, PopularItemReport, CustomerAnalytics


@admin.register(DailySalesReport)
class DailySalesReportAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'report_date', 'total_sales', 'total_orders', 'completed_orders']
    list_filter = ['report_date', 'restaurant']
    search_fields = ['restaurant__name']


@admin.register(PopularItemReport)
class PopularItemReportAdmin(admin.ModelAdmin):
    list_display = ['menu_item', 'restaurant', 'report_date', 'times_ordered', 'total_revenue']
    list_filter = ['report_date', 'restaurant']


@admin.register(CustomerAnalytics)
class CustomerAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['customer', 'restaurant', 'total_orders', 'total_spent', 'is_returning_customer']
    list_filter = ['is_returning_customer', 'restaurant']