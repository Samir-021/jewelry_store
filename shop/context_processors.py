from .models import Category, Cart

def navbar_categories(request):
    return {
        "navbar_main_categories": Category.objects.filter(parent__isnull=True)
        .prefetch_related("children")
    }

def cart_count(request):
    count = 0

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart = Cart.objects.filter(session_key=session_key).first()
    if cart:
        count = cart.items.count()

    return {
        "cart_count": count
    }