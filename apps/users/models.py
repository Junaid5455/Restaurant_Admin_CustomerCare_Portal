from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import secrets

from apps.common.models import BaseModel
from apps.common.choices import USER_ROLES, GENDER_CHOICES


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "SUPER_ADMIN")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("Email Address"), unique=True, db_index=True)
    phone = models.CharField(_("Phone Number"), max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(_("Profile Picture"), upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(_("Bio"), blank=True, null=True)
    role = models.CharField(_("Role"), max_length=20, choices=USER_ROLES, default='CUSTOMER')
    
    # New fields for verification
    email_verified = models.BooleanField(_("Email Verified"), default=False)
    email_verified_at = models.DateTimeField(_("Email Verified At"), null=True, blank=True)
    last_password_changed = models.DateTimeField(_("Last Password Changed"), null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def is_restaurant_owner(self):
        return self.role == 'RESTAURANT_OWNER'

    def is_customer(self):
        return self.role == 'CUSTOMER'

    def is_delivery_staff(self):
        return self.role == 'DELIVERY_STAFF'

    def is_restaurant_staff(self):
        return self.role == 'RESTAURANT_STAFF'


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(_("Date of Birth"), null=True, blank=True)
    gender = models.CharField(_("Gender"), max_length=20, choices=GENDER_CHOICES, default='NOT_SPECIFIED')
    address = models.TextField(_("Address"), blank=True, null=True)
    city = models.CharField(_("City"), max_length=100, blank=True, null=True)
    state = models.CharField(_("State"), max_length=100, blank=True, null=True)
    country = models.CharField(_("Country"), max_length=100, blank=True, null=True)
    postal_code = models.CharField(_("Postal Code"), max_length=10, blank=True, null=True)
    loyalty_points = models.IntegerField(_("Loyalty Points"), default=0)
    total_orders = models.IntegerField(_("Total Orders"), default=0)
    total_spent = models.DecimalField(_("Total Spent"), max_digits=10, decimal_places=2, default=0)
    preferred_payment_method = models.CharField(_("Preferred Payment Method"), max_length=50, blank=True, null=True)
    notification_email = models.BooleanField(_("Email Notifications"), default=True)
    notification_sms = models.BooleanField(_("SMS Notifications"), default=True)
    notification_push = models.BooleanField(_("Push Notifications"), default=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"

    def increment_loyalty_points(self, points):
        self.loyalty_points += points
        self.save(update_fields=['loyalty_points'])
        return self.loyalty_points

    def increment_order_count_and_spent(self, amount):
        self.total_orders += 1
        self.total_spent += amount
        self.save(update_fields=['total_orders', 'total_spent'])


# ====================================================
# Token Models for Email Verification & Password Reset
# ====================================================

class EmailVerificationToken(BaseModel):
    """Tokens for email verification"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='email_verification_token'
    )
    token = models.CharField(max_length=255, unique=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'users_email_verification_token'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Email verification token for {self.user.email}"
    
    def is_expired(self):
        """Check if token has expired"""
        return timezone.now() > self.expires_at
    
    @staticmethod
    def generate_token():
        """Generate secure random token"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def create_for_user(cls, user):
        """Create or update verification token for user"""
        token = cls.generate_token()
        expires_at = timezone.now() + timedelta(days=1)
        
        obj, created = cls.objects.update_or_create(
            user=user,
            defaults={
                'token': token,
                'is_used': False,
                'used_at': None,
                'expires_at': expires_at
            }
        )
        return obj


class PasswordResetToken(BaseModel):
    """Tokens for password reset"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens'
    )
    token = models.CharField(max_length=255, unique=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'users_password_reset_token'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Password reset token for {self.user.email}"
    
    def is_expired(self):
        """Check if token has expired"""
        return timezone.now() > self.expires_at
    
    @staticmethod
    def generate_token():
        """Generate secure random token"""
        return secrets.token_urlsafe(32)
    
    @classmethod
    def create_for_user(cls, user):
        """Create password reset token for user"""
        token = cls.generate_token()
        expires_at = timezone.now() + timedelta(hours=2)
        
        # Invalidate previous tokens
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        
        obj = cls.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        return obj