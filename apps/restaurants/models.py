from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from apps.common.models import BaseModel
from apps.users.models import User
from apps.common.choices import STAFF_ROLES


class Restaurant(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='restaurant_logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='restaurant_banners/', blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_open = models.BooleanField(default=True)
    min_order_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    delivery_time_minutes = models.IntegerField(default=30)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    website = models.URLField(blank=True, null=True)
    allows_pickup = models.BooleanField(default=True)
    allows_delivery = models.BooleanField(default=True)
    allows_dine_in = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Restaurants"
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def clean(self):
        if self.opening_time and self.closing_time and self.opening_time >= self.closing_time:
            raise ValidationError("Closing time must be after opening time.")

    def is_open_now(self):
        from django.utils import timezone
        now = timezone.now().time()
        return self.is_active and self.opening_time <= now <= self.closing_time


class RestaurantHoliday(BaseModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='holidays')
    holiday_date = models.DateField()
    reason = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.holiday_date}"


class RestaurantDeliveryZone(BaseModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='delivery_zones')
    zone_name = models.CharField(max_length=100)
    delivery_fee = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_time_minutes = models.IntegerField()
    postal_codes = models.TextField(help_text="Comma-separated postal codes")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.zone_name} - {self.restaurant.name}"


class RestaurantStaffMember(BaseModel):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='staff_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_profiles')
    role = models.CharField(max_length=20, choices=STAFF_ROLES)
    is_active = models.BooleanField(default=True)
    can_manage_menu = models.BooleanField(default=False)
    can_manage_orders = models.BooleanField(default=False)
    can_manage_staff = models.BooleanField(default=False)
    can_manage_payments = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.restaurant.name}"

    def has_permission(self, permission_name):
        return getattr(self, permission_name, False)

    def assign_role(self, new_role):
        self.role = new_role
        self.save()