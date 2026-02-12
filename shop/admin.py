from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Product, ProductImage, CustomOrder


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    prepopulated_fields = {"slug": ("name",)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "category", "price", "metal",
        "gender", "stone", "brand", "available"
    )
    list_filter = ("category", "metal", "gender", "stone", "color", "available")
    search_fields = ("name", "brand")


@admin.register(CustomOrder)
class CustomOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "status", "created_at")
    list_filter = ("status", "created_at")
