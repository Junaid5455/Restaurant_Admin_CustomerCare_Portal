from rest_framework import serializers
from apps.menu.models import MenuCategory, MenuItem, MenuItemCustomization, MenuItemCustomizationOption, MenuItemAddOn

class MenuItemCustomizationOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemCustomizationOption
        fields = ['id', 'name', 'price_modifier', 'order']

class MenuItemCustomizationSerializer(serializers.ModelSerializer):
    options = MenuItemCustomizationOptionSerializer(many=True, read_only=True)
    
    class Meta:
        model = MenuItemCustomization
        fields = ['id', 'name', 'type', 'is_required', 'options']

class MenuItemAddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemAddOn
        fields = ['id', 'name', 'price', 'is_available']

class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'description', 'image', 'order', 'is_active']

class MenuCategoryDetailSerializer(MenuCategorySerializer):
    items = serializers.SerializerMethodField()
    
    class Meta(MenuCategorySerializer.Meta):
        fields = MenuCategorySerializer.Meta.fields + ['items']
    
    def get_items(self, obj):
        items = obj.items.filter(is_available=True)
        return MenuItemSerializer(items, many=True).data

class MenuItemSerializer(serializers.ModelSerializer):
    review_count = serializers.IntegerField(source='total_reviews', read_only=True)
    prep_time = serializers.IntegerField(source='preparation_time_minutes', read_only=True)
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'price', 'image', 'prep_time', 
            'is_available', 'is_featured', 'rating', 'review_count'
        ]

class MenuItemDetailSerializer(serializers.ModelSerializer):
    review_count = serializers.IntegerField(source='total_reviews', read_only=True)
    prep_time = serializers.IntegerField(source='preparation_time_minutes', read_only=True)
    customizations = MenuItemCustomizationSerializer(many=True, read_only=True)
    add_ons = MenuItemAddOnSerializer(many=True, read_only=True)
    category = MenuCategorySerializer(read_only=True)
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'price', 'image', 'prep_time', 
            'is_available', 'is_featured', 'is_spicy', 'is_vegetarian', 'is_vegan', 
            'calories', 'rating', 'review_count', 'customizations', 'add_ons', 'category'
        ]