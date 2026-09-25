"""
Base serializer classes for the Restaurant Portal API.
"""
from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    """
    Base serializer for all model serializers.

    Includes read-only timestamp fields and standard error
    message formatting.
    """

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        abstract = True
        read_only_fields = ("id", "created_at", "updated_at")


class TimestampSerializerMixin(serializers.Serializer):
    """
    Mixin to add timestamp fields to any serializer.

    Usage:
        class MySerializer(TimestampSerializerMixin, serializers.Serializer):
            ...
    """

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        abstract = True
        fields = ("id", "created_at", "updated_at")


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    ModelSerializer that takes an additional `fields` argument
    to dynamically control which fields are included.

    Usage:
        class MySerializer(DynamicFieldsModelSerializer):
            ...
        # Then in the view:
        serializer = MySerializer(obj, fields=('id', 'name'))
    """

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)

        super().__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)