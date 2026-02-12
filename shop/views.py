from django.views.generic import ListView, DetailView
from unicodedata import category
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, CartItem,  Cart, Order, OrderItem, Category
from .utils import get_cart, generate_signature
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import base64
import hashlib
import hmac

def home(request):
    products = Product.objects.all()[:6]  # Fetch 6 products
    return render(request, "shop/home.html", {"products": products})

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            raise forms.ValidationError("Passwords do not match")
        return cleaned

def product_list(request):
    products = Product.objects.filter(available=True)

    # Category filter
    category_slug = request.GET.get("category")
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        if category.children.exists():
            products = products.filter(category__in=category.children.all())
        else:
            products = products.filter(category=category)
    else:
        category = None

    # Price filters (SAFE parsing)
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    FILTER_FIELDS = [
        "metal",
        "gender",
        "stone",
        "necklace_style",
        "brand",
        "color",
    ]

    for field in FILTER_FIELDS:
        value = request.GET.get(field)
        if value:
            products = products.filter(**{field: value})

    try:
        if min_price:
            products = products.filter(price__gte=Decimal(min_price))
        if max_price:
            products = products.filter(price__lte=Decimal(max_price))
    except InvalidOperation:
        pass  # ignore invalid input safely

    context = {
        "products": products,
        "category": category,
        "min_price": min_price,
        "max_price": max_price,
        "active_filters": request.GET,
    }

    return render(request, "shop/product_list.html", context)

class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product_detail.html"
    context_object_name = "product"
    pk_url_kwarg = "id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Fetch related products: Same category, exclude current, limit 4
        related_products = Product.objects.filter(
            category=product.category,
            available=True
        ).exclude(id=product.id)[:4]
        
        context['related_products'] = related_products
        return context

def add_to_cart(request, product_id):
    if request.method != "POST":
        return redirect("shop:product_detail", product_id)

    product = get_object_or_404(Product, id=product_id)
    ring_size = request.POST.get("ring_size")

    is_ring = (
        product.category.slug == "rings" or
        (product.category.parent and product.category.parent.slug == "rings")
    )

    if is_ring and not ring_size:
        messages.error(request, "Please select a ring size.")
        return redirect("shop:product_detail", product.slug)

    cart = get_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        ring_size=ring_size if is_ring else None,
    )

    if not created:
        item.quantity += 1
        item.save()

    messages.success(request, "Item added to cart.")
    return redirect("shop:cart")

def cart_detail(request):
    cart = get_cart(request)
    return render(request, "shop/cart.html", {"cart": cart})

def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    action = request.POST.get("action")

    if action == "increase":
        item.quantity += 1
    elif action == "decrease" and item.quantity > 1:
        item.quantity -= 1

    item.save()
    return redirect("shop:cart")

def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect("shop:cart")

@login_required
def checkout(request):
    cart = Cart.objects.get(session_key=request.session.session_key)

    if not cart.items.exists():
        return redirect("shop:cart")

    order = Order.objects.create(
        user=request.user,
        total_amount=cart.total_price()
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            ring_size=item.ring_size,
            quantity=item.quantity,
            price=item.product.price
        )

    return redirect("shop:esewa_pay", order_id=order.order_id)

def esewa_pay(request, order_id):
    order = Order.objects.get(order_id=order_id)

    total_amount = format(order.total_amount, ".2f")
    transaction_uuid = str(order.order_id)
    product_code = "EPAYTEST"

    signed_fields = "total_amount,transaction_uuid,product_code"

    secret_key = "8gBm/:&EnhH.1/q"

    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    print("ESewa Message:", message)
    print("Amount:", total_amount)
    print("ORDER TOTAL FROM DB:", order.total_amount)

    signature = base64.b64encode(
        hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    context = {
        "order": order,
        "amount": total_amount,
        "tax_amount": "0.00",
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "product_code": product_code,
        "product_service_charge": "0.00",
        "product_delivery_charge": "0.00",
        "success_url": "https://postamniotic-fermin-dentally.ngrok-free.dev/payment/success/",
        "failure_url": "https://postamniotic-fermin-dentally.ngrok-free.dev/payment/failure/",
        "signed_field_names": signed_fields,
        "signature": signature,
    }

    return render(request, "shop/esewa_pay.html", context)

import json
import base64

def payment_success(request):
    encoded_data = request.POST.get("data")

    if not encoded_data:
        return render(request, "shop/payment_failed.html")

    # Decode base64
    decoded_bytes = base64.b64decode(encoded_data)
    decoded_str = decoded_bytes.decode("utf-8")
    response_data = json.loads(decoded_str)

    print("DECODED RESPONSE:", response_data)

    status = response_data.get("status")
    transaction_uuid = response_data.get("transaction_uuid")
    received_signature = response_data.get("signature")
    product_code = response_data.get("product_code")

    order = get_object_or_404(Order, order_id=transaction_uuid)

    secret_key = "8gBm/:&EnhH.1/q"

    message = f"total_amount={response_data.get('total_amount')},transaction_uuid={transaction_uuid},product_code={product_code}"

    generated_signature = base64.b64encode(
        hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    print("GENERATED:", generated_signature)
    print("RECEIVED:", received_signature)

    if generated_signature == received_signature and status == "COMPLETE":
        order.status = "paid"
        order.save()
        return render(request, "shop/payment_success.html", {"order": order})

    return render(request, "shop/payment_failed.html")

def payment_failure(request):
    order_id = request.GET.get("transaction_uuid")

    if order_id:
        try:
            order = Order.objects.get(order_id=order_id)
            order.status = "failed"
            order.save()
        except Order.DoesNotExist:
            pass

    return render(request, "shop/payment_failed.html")
