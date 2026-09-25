from django.db import models
from apps.common.models import BaseModel
from apps.users.models import User
from apps.restaurants.models import Restaurant
from apps.menu.models import MenuItem


class DailySalesReport(BaseModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='daily_reports')
    report_date = models.DateField()
    total_orders = models.IntegerField(default=0)
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_customers = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    total_refunds = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cancelled_orders = models.IntegerField(default=0)
    completed_orders = models.IntegerField(default=0)
    average_preparation_time_minutes = models.IntegerField(default=0)
    average_delivery_time_minutes = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('restaurant', 'report_date')
        ordering = ['-report_date']

    def __str__(self):
        return f"{self.restaurant.name} - {self.report_date}"


class PopularItemReport(BaseModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='popular_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    report_date = models.DateField()
    times_ordered = models.IntegerField(default=0)
    total_quantity_sold = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('restaurant', 'menu_item', 'report_date')
        ordering = ['-report_date', '-times_ordered']

    def __str__(self):
        return f"{self.menu_item.name} - {self.report_date}"


class CustomerAnalytics(BaseModel):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_order_date = models.DateField(null=True, blank=True)
    days_since_last_order = models.IntegerField(null=True, blank=True)
    customer_lifetime_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_returning_customer = models.BooleanField(default=False)

    class Meta:
        unique_together = ('customer', 'restaurant')

    def __str__(self):
        return f"{self.customer.email} - {self.restaurant.name}"

    def calculate_metrics(self):
        if self.total_orders > 0:
            self.average_order_value = self.total_spent / self.total_orders
            self.customer_lifetime_value = self.total_spent
            self.is_returning_customer = self.total_orders > 1
        self.save()