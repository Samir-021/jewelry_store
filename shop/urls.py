from django.urls import path
from .views import ProductDetailView
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.product_list, name="product_list"),
    path("product/<int:id>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_detail, name="cart"),
    path("cart/update/<int:item_id>/", views.update_cart_item, name="update_cart_item"),
    path("cart/remove/<int:item_id>/", views.remove_cart_item, name="remove_cart_item"),
    path("checkout/", views.checkout, name="checkout"),
    path("esewa/<uuid:order_id>/", views.esewa_pay, name="esewa_pay"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/failure/", views.payment_failure, name="payment_failure"),
    path("stores/", views.stores, name="stores"),
    path("api/nearby-stores/", views.nearby_stores_api, name="nearby_stores_api"),

    # Vendor URLs
    path("vendor/login/", views.vendor_login, name="vendor_login"),
    path("vendor/register/", views.vendor_register, name="vendor_register"),
    path("vendor/dashboard/", views.vendor_dashboard, name="vendor_dashboard"),
    path("vendor/products/", views.vendor_product_list, name="vendor_product_list"),
    path("vendor/products/add/", views.vendor_add_product, name="vendor_add_product"),
    path("vendor/products/edit/<slug:slug>/", views.vendor_edit_product, name="vendor_edit_product"),
    path("vendor/products/delete/<slug:slug>/", views.vendor_delete_product, name="vendor_delete_product"),

]