from django.db import models
from apps.common.models import BaseModel
from apps.restaurants.models import Restaurant
from apps.common.choices import CUSTOMIZATION_TYPES


class MenuCategory(BaseModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Menu Categories"
        unique_together = ('restaurant', 'name')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class MenuItem(BaseModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    category = models.ForeignKey(MenuCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    preparation_time_minutes = models.IntegerField(default=15)
    calories = models.IntegerField(blank=True, null=True)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    contains_nuts = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    in_stock = models.BooleanField(default=True)
    total_orders = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)

    class Meta:
        unique_together = ('restaurant', 'name')
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['restaurant']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        return self.name

    def mark_unavailable(self):
        self.is_available = False
        self.save(update_fields=['is_available'])

    def mark_available(self):
        self.is_available = True
        self.save(update_fields=['is_available'])

    def mark_out_of_stock(self):
        self.in_stock = False
        self.save(update_fields=['in_stock'])

    def mark_in_stock(self):
        self.in_stock = True
        self.save(update_fields=['in_stock'])

    def increment_order_count(self):
        self.total_orders += 1
        self.save(update_fields=['total_orders'])


class MenuItemCustomization(BaseModel):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='customizations')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=CUSTOMIZATION_TYPES)
    is_required = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class MenuItemCustomizationOption(BaseModel):
    customization = models.ForeignKey(MenuItemCustomization, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)
    price_modifier = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class MenuItemAddOn(BaseModel):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='addons')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name