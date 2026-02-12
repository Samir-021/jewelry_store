from django.db import models
from django.contrib.auth.models import User
import uuid
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        blank=True,
        null=True
    )
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    GENDER_CHOICES = [
        ("men", "Men"),
        ("women", "Women"),
        ("unisex", "Unisex"),
    ]

    METAL_CHOICES = [
        ("gold", "Gold"),
        ("silver", "Silver"),
        ("platinum", "Platinum"),
    ]

    STONE_CHOICES = [
        ("diamond", "Diamond"),
        ("ruby", "Ruby"),
        ("emerald", "Emerald"),
        ("none", "No Stone"),
    ]

    COLOR_CHOICES = [
        ("yellow", "Yellow"),
        ("white", "White"),
        ("rose", "Rose"),
        ("black", "Black"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)

    metal = models.CharField(max_length=20, choices=METAL_CHOICES, blank=True, db_index=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, db_index=True)
    stone = models.CharField(max_length=20, choices=STONE_CHOICES, blank=True, db_index=True)
    necklace_style = models.CharField(max_length=50, blank=True)
    brand = models.CharField(max_length=50, blank=True, db_index=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, blank=True, db_index=True)

    image = models.ImageField(upload_to="products/%Y/%m/%d/", blank=True, null=True)
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    ring_size_required = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/extra/%Y/%m/%d/")

    def __str__(self):
        return f"Image for {self.product.name}"


class CustomOrder(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Custom Order #{self.id}"

class Cart(models.Model):
    session_key = models.CharField(max_length=40, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ring_size = models.CharField(max_length=10, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product", "ring_size")

    def subtotal(self):
        return self.product.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order_id)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ring_size = models.CharField(max_length=10, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity