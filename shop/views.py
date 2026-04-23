from django.views.generic import ListView, DetailView
from unicodedata import category
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, CartItem,  Cart, Order, OrderItem, Category, Store
from .utils import get_cart, generate_signature
from .slug_utils import generate_unique_slug
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import StoreRegistrationForm, UnifiedVendorRegistrationForm, VendorProductForm
from django.utils.text import slugify
import hmac
import requests
from django.http import JsonResponse
import json
import base64
import hashlib

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
    from django.db.models import Q
    # Public must see products from verified stores OR products with no store (official)
    products = Product.objects.filter(
        Q(available=True) & (Q(store__isnull=True) | Q(store__verification_status='verified'))
    )

    # Search Filter
    query = request.GET.get("q")
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Location Filter
    location = request.GET.get("location")
    if location:
        products = products.filter(store__city__iexact=location)

    # Get distinct cities for dropdown
    cities = Store.objects.filter(verification_status='verified').values_list('city', flat=True).distinct().order_by('city')

    # Category filter
    category_slug = request.GET.get("category")
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        # Include current category and all its children
        category_ids = [category.id] + list(category.children.values_list('id', flat=True))
        products = products.filter(category_id__in=category_ids)
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
        "cities": cities, # Pass cities to template
        "current_location": location,
    }

    return render(request, "shop/product_list.html", context)

class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product_detail.html"
    context_object_name = "product"
    pk_url_kwarg = "id"

    def get_queryset(self):
        from django.db.models import Q
        return super().get_queryset().filter(
            Q(available=True) & (Q(store__isnull=True) | Q(store__verification_status='verified'))
        )

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

    from django.conf import settings
    secret_key = getattr(settings, "ESEWA_SECRET_KEY", "8gBm/:&EnhH.1/q")

    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    
    signature = base64.b64encode(
        hmac.new(
            secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
    ).decode()

    # Build absolute URLs
    success_url = request.build_absolute_uri('/payment/success/')
    failure_url = request.build_absolute_uri('/payment/failure/')

    context = {
        "order": order,
        "amount": total_amount,
        "tax_amount": "0.00",
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "product_code": product_code,
        "product_service_charge": "0.00",
        "product_delivery_charge": "0.00",
        "success_url": success_url,
        "failure_url": failure_url,
        "signed_field_names": signed_fields,
        "signature": signature,
    }

    return render(request, "shop/esewa_pay.html", context)

import json
import base64

def payment_success(request):
    # eSewa v2 success redirect is usually a GET request with 'data' parameter
    encoded_data = request.GET.get("data") or request.POST.get("data")

    if not encoded_data:
        return render(request, "shop/payment_failed.html")

    try:
        # Decode base64
        decoded_bytes = base64.b64decode(encoded_data)
        decoded_str = decoded_bytes.decode("utf-8")
        response_data = json.loads(decoded_str)
    except Exception as e:
        print(f"Error decoding eSewa response: {e}")
        return render(request, "shop/payment_failed.html")

    print("DECODED RESPONSE:", response_data)

    status = response_data.get("status")
    transaction_uuid = response_data.get("transaction_uuid")
    received_signature = response_data.get("signature")
    signed_field_names = response_data.get("signed_field_names")

    if not all([status, transaction_uuid, received_signature, signed_field_names]):
        return render(request, "shop/payment_failed.html")

    order = get_object_or_404(Order, order_id=transaction_uuid)

    # Use secret key from settings if available
    from django.conf import settings
    secret_key = getattr(settings, "ESEWA_SECRET_KEY", "8gBm/:&EnhH.1/q")

    # Construct message based on signed_field_names
    fields = signed_field_names.split(',')
    message_parts = []
    for field in fields:
        value = response_data.get(field)
        message_parts.append(f"{field}={value}")
    
    message = ",".join(message_parts)
    print("VERIFICATION MESSAGE:", message)

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
        # Also clear the cart
        from .utils import get_cart
        cart = get_cart(request)
        cart.items.all().delete()
        
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

def stores(request):
    """Renders the nearby stores page."""
    return render(request, "shop/stores.html")

def nearby_stores_api(request):
    """
    Fetches nearby jewelry stores using OpenStreetMap's Overpass API.
    Expects 'lat' and 'lon' as GET parameters.
    """
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")
    radius_input = request.GET.get("radius", 5000)

    try:
        radius = int(radius_input)
    except ValueError:
        radius = 5000

    if not lat or not lon:
        return JsonResponse({"error": "Missing latitude or longitude"}, status=400)

    try:
        # Overpass QL query: Find nodes with shop=jewelry within radius

        overpass_url = "https://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        (
          node["shop"="jewelry"](around:{radius},{lat},{lon});
          way["shop"="jewelry"](around:{radius},{lat},{lon});
          relation["shop"="jewelry"](around:{radius},{lat},{lon});
        );
        out center;
        """
        
        # User-Agent header is often required by Overpass API
        headers = {'User-Agent': 'JewelryStoreApp/1.0'}
        response = requests.get(overpass_url, params={'data': overpass_query}, headers=headers, timeout=25)
        response.raise_for_status()
        data = response.json()

        stores = []
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            
            # Determine coordinates (center for ways/relations, lat/lon for nodes)
            if "lat" in element and "lon" in element:
                store_lat = element["lat"]
                store_lon = element["lon"]
            elif "center" in element:
                store_lat = element["center"]["lat"]
                store_lon = element["center"]["lon"]
            else:
                continue # Skip if no coords

            stores.append({
                "name": tags.get("name", "Unknown Jewelry Store"),
                "address": tags.get("addr:street", "") + " " + tags.get("addr:housenumber", ""),
                "lat": store_lat,
                "lon": store_lon,
                "brand": tags.get("brand", ""),
                "phone": tags.get("phone", tags.get("contact:phone", "")),
                "opening_hours": tags.get("opening_hours", ""),
            })

        return JsonResponse({"stores": stores})

    except Exception as e:
        print(f"Overpass API Error: {e}")
        return JsonResponse({"error": f"Failed to fetch nearby stores: {str(e)}"}, status=503)


def vendor_login(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'store'):
            return redirect('shop:vendor_dashboard')
        return redirect('shop:home')
    
    if request.method == 'POST':
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            from django.contrib.auth import authenticate, login
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if hasattr(user, 'store'):
                    return redirect('shop:vendor_dashboard')
                return redirect('shop:vendor_register')
    else:
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm()
    
    return render(request, 'shop/vendor/vendor_login.html', {'form': form})

def vendor_register(request):
    if request.user.is_authenticated and hasattr(request.user, 'store'):
        return redirect('shop:vendor_dashboard')

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = StoreRegistrationForm(request.POST)
        else:
            form = UnifiedVendorRegistrationForm(request.POST)
            
        if form.is_valid():
            from django.contrib.auth.models import User
            from django.db import transaction
            from django.contrib.auth import login
            
            with transaction.atomic():
                if not request.user.is_authenticated:
                    user_email = form.cleaned_data.get('user_email')
                    password = form.cleaned_data.get('password')
                    # Use email as username for convenience in this vendor flow
                    user = User.objects.create_user(username=user_email, email=user_email, password=password)
                    login(request, user)
                else:
                    user = request.user
                
                store = form.save(commit=False)
                store.user = user
                store.save()
                
            messages.success(request, "Registration successful! Welcome to the vendor portal.")
            return redirect('shop:vendor_dashboard')
    else:
        if request.user.is_authenticated:
            form = StoreRegistrationForm()
        else:
            form = UnifiedVendorRegistrationForm()
    
    return render(request, 'shop/vendor/register.html', {'form': form, 'base_template': 'shop/base.html'})

@login_required
def vendor_dashboard(request):
    if not hasattr(request.user, 'store'):
        return redirect('shop:vendor_register')
    
    store = request.user.store
    products = store.products.all()
    return render(request, 'shop/vendor/dashboard.html', {'store': store, 'products': products, 'base_template': 'shop/vendor/vendor_admin_base.html'})

@login_required
def vendor_product_list(request):
    if not hasattr(request.user, 'store'):
        return redirect('shop:vendor_register')
    
    products = request.user.store.products.all()
    return render(request, 'shop/vendor/product_list.html', {'products': products, 'base_template': 'shop/vendor/vendor_admin_base.html'})

@login_required
def vendor_add_product(request):
    if not hasattr(request.user, 'store'):
        return redirect('shop:vendor_register')
    
    store = request.user.store
    if store.verification_status != 'verified':
        messages.error(request, "Your store must be verified to add products.")
        return redirect('shop:vendor_dashboard')

    if request.method == 'POST':
        form = VendorProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            
            # --- Dynamic Category Logic ---
            new_cat = form.cleaned_data.get('new_category_name')
            new_sub = form.cleaned_data.get('new_subcategory_name')
            existing_cat = form.cleaned_data.get('category')
            
            target_category = existing_cat
            
            if new_cat:
                parent_cat, created = Category.objects.get_or_create(
                    name=new_cat.strip(),
                    defaults={'slug': generate_unique_slug(new_cat)}
                )
                target_category = parent_cat
                
                if new_sub:
                    sub_cat, created = Category.objects.get_or_create(
                        name=new_sub.strip(),
                        parent=parent_cat,
                        defaults={'slug': generate_unique_slug(f"{new_cat}-{new_sub}")}
                    )
                    target_category = sub_cat
            elif new_sub:
                # Sub-category without a parent? 
                # If existing_cat selected, use it as parent. Else error?
                if existing_cat:
                    sub_cat, created = Category.objects.get_or_create(
                        name=new_sub.strip(),
                        parent=existing_cat,
                        defaults={'slug': generate_unique_slug(f"{existing_cat.name}-{new_sub}")}
                    )
                    target_category = sub_cat
                else:
                    # Treat as a top-level category if no parent specified
                    sub_cat, created = Category.objects.get_or_create(
                        name=new_sub.strip(),
                        defaults={'slug': generate_unique_slug(new_sub)}
                    )
                    target_category = sub_cat
            
            if not target_category:
                messages.error(request, "Please select or create a category.")
                return render(request, 'shop/vendor/product_form.html', {'form': form, 'title': 'Add Product', 'base_template': 'shop/vendor/vendor_admin_base.html'})
            
            product.category = target_category
            # ------------------------------

            product.slug = generate_unique_slug(product.name)
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect('shop:vendor_product_list')
    else:
        form = VendorProductForm()

    return render(request, 'shop/vendor/product_form.html', {'form': form, 'title': 'Add Product', 'base_template': 'shop/vendor/vendor_admin_base.html'})

@login_required
def vendor_edit_product(request, slug):
    if not hasattr(request.user, 'store'):
        return redirect('shop:vendor_register')
    
    product = get_object_or_404(Product, slug=slug, store=request.user.store)

    if request.method == 'POST':
        form = VendorProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            
            # --- Dynamic Category Logic (Same as add) ---
            new_cat = form.cleaned_data.get('new_category_name')
            new_sub = form.cleaned_data.get('new_subcategory_name')
            existing_cat = form.cleaned_data.get('category')
            
            target_category = existing_cat
            
            if new_cat:
                parent_cat, created = Category.objects.get_or_create(
                    name=new_cat.strip(),
                    defaults={'slug': generate_unique_slug(new_cat)}
                )
                target_category = parent_cat
                
                if new_sub:
                    sub_cat, created = Category.objects.get_or_create(
                        name=new_sub.strip(),
                        parent=parent_cat,
                        defaults={'slug': generate_unique_slug(f"{new_cat}-{new_sub}")}
                    )
                    target_category = sub_cat
            elif new_sub:
                if existing_cat:
                    sub_cat, created = Category.objects.get_or_create(
                        name=new_sub.strip(),
                        parent=existing_cat,
                        defaults={'slug': generate_unique_slug(f"{existing_cat.name}-{new_sub}")}
                    )
                    target_category = sub_cat
                else:
                    sub_cat, created = Category.objects.get_or_create(
                        name=new_sub.strip(),
                        defaults={'slug': generate_unique_slug(new_sub)}
                    )
                    target_category = sub_cat
            
            if target_category:
                product.category = target_category
            
            # ------------------------------
            
            product.save()
            messages.success(request, "Product updated successfully!")
            return redirect('shop:vendor_product_list')
    else:
        form = VendorProductForm(instance=product)

    return render(request, 'shop/vendor/product_form.html', {'form': form, 'title': 'Edit Product', 'base_template': 'shop/vendor/vendor_admin_base.html'})

@login_required
def vendor_delete_product(request, slug):
    if not hasattr(request.user, 'store'):
        return redirect('shop:vendor_register')

    # Strict filtering: Must belong to user's store
    product = get_object_or_404(Product, slug=slug, store=request.user.store)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('shop:vendor_product_list')
    
    return render(request, 'shop/vendor/product_confirm_delete.html', {'product': product, 'base_template': 'shop/vendor/vendor_admin_base.html'})
