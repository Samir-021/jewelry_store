from .models import Cart
import hmac
import hashlib
import base64

def get_cart(request):
    if not request.session.session_key:
        request.session.create()

    cart, _ = Cart.objects.get_or_create(
        session_key=request.session.session_key
    )
    return cart

def generate_signature(total_amount, transaction_uuid, product_code):
    secret_key = "8gBm/:&EnhH.1/q"  # UAT key

    message = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"

    hmac_sha256 = hmac.new(
        secret_key.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    )

    digest = hmac_sha256.digest()
    signature = base64.b64encode(digest).decode("utf-8")

    return signature