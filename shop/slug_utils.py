import uuid
from django.utils.text import slugify

def generate_unique_slug(name):
    """
    Generates a unique slug using the name and a short UUID.
    Example: 'Gold Ring' -> 'gold-ring-a1b2c3d4'
    """
    short_uuid = str(uuid.uuid4())[:8]
    return f"{slugify(name)}-{short_uuid}"
