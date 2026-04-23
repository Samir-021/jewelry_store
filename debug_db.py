import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jewelry_site.settings')
django.setup()

from shop.models import Store, Category, Product

print("--- STORES ---")
for store in Store.objects.all():
    print(f"Store: {store.store_name}, Status: {store.verification_status}")

print("\n--- CATEGORIES ---")
for cat in Category.objects.all():
    parent_name = cat.parent.name if cat.parent else "None"
    print(f"Category: {cat.name} (Slug: {cat.slug}), Parent: {parent_name}")

print("\n--- PRODUCTS ---")
for prod in Product.objects.all():
    store_status = prod.store.verification_status if prod.store else "No Store"
    print(f"Product: {prod.name}, Category: {prod.category.name}, Store Status: {store_status}")
