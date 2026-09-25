"""
Abstract base models for the Restaurant Portal project.

All app models should inherit from these to ensure consistency
in primary keys, timestamps, and soft-delete functionality.
"""
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    Abstract base class providing self-updating created_at and updated_at fields.

    Usage:
        class MyModel(TimeStampedModel):
            ...
    """

    created_at = models.DateTimeField(
        _("Created At"), auto_now_add=True, db_index=True
    )
    updated_at = models.DateTimeField(
        _("Updated At"), auto_now=True, db_index=True
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class UUIDModel(models.Model):
    """
    Abstract base class providing a UUID primary key.

    UUIDs are useful when:
        - You need globally unique identifiers across tables
        - You don't want to expose sequential IDs in URLs
        - You're using database sharding
    """

    id = models.UUIDField(
        _("ID"),
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel):
    """
    Abstract base model combining UUID primary key and timestamps.

    All domain models should inherit from this:
        class MenuItem(BaseModel):
            ...
    """

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteModel(models.Model):
    """
    Abstract base class providing soft-delete functionality.

    Instead of actually deleting records, they are marked as deleted
    and excluded from default querysets.
    """

    is_deleted = models.BooleanField(
        _("Is Deleted"), default=False, db_index=True
    )
    deleted_at = models.DateTimeField(
        _("Deleted At"), null=True, blank=True, db_index=True
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark the instance as deleted."""
        from django.utils import timezone

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def restore(self):
        """Restore a soft-deleted instance."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])


class FullBaseModel(BaseModel, SoftDeleteModel):
    """
    Complete base model with UUID, timestamps, and soft delete.

    Use this for all primary domain models:
        class Order(FullBaseModel):
            ...
    """

    class Meta:
        abstract = True
        ordering = ["-created_at"]