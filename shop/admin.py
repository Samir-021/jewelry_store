from django.contrib import admin
from .models import Category, Product, ProductImage, CustomOrder, Store


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
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("store_name", "owner_name", "city", "verification_status", "created_at")
    list_filter = ("verification_status", "city", "province")
    search_fields = ("store_name", "owner_name", "email")
    actions = ["approve_stores", "reject_stores"]

    @admin.action(description="Approve selected stores")
    def approve_stores(self, request, queryset):
        rows_updated = queryset.update(verification_status="verified")
        if rows_updated == 1:
            message_bit = "1 store was"
        else:
            message_bit = f"{rows_updated} stores were"
        self.message_user(request, f"{message_bit} successfully marked as verified.")

    @admin.action(description="Reject selected stores")
    def reject_stores(self, request, queryset):
        rows_updated = queryset.update(verification_status="rejected")
        if rows_updated == 1:
            message_bit = "1 store was"
        else:
            message_bit = f"{rows_updated} stores were"
        self.message_user(request, f"{message_bit} marked as rejected.")
