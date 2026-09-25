from django.contrib import admin
from .models import MenuCategory, MenuItem, MenuItemCustomization, MenuItemCustomizationOption, MenuItemAddOn


class MenuItemCustomizationOptionInline(admin.TabularInline):
    model = MenuItemCustomizationOption
    extra = 1


class MenuItemCustomizationInline(admin.TabularInline):
    model = MenuItemCustomization
    extra = 1


class MenuItemAddOnInline(admin.TabularInline):
    model = MenuItemAddOn
    extra = 1


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'order', 'is_active']
    list_filter = ['is_active', 'restaurant']
    search_fields = ['name', 'restaurant__name']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'category', 'price', 'is_available', 'in_stock']
    list_filter = ['is_available', 'in_stock', 'is_vegetarian', 'is_vegan']
    search_fields = ['name', 'description', 'restaurant__name']
    inlines = [MenuItemCustomizationInline, MenuItemAddOnInline]