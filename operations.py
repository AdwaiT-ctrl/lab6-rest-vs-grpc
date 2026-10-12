"""Shared calculations so REST and gRPC perform the same work."""
import base64
import binascii
import io
import math
from PIL import Image, UnidentifiedImageError


def dot_product(a, b):
    if not isinstance(a, (list, tuple)) or not isinstance(b, (list, tuple)):
        raise ValueError("a and b must be numeric lists")
    if len(a) != len(b):
        raise ValueError("a and b must have the same length")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x)
           for x in (*a, *b)):
        raise ValueError("vectors must contain finite numbers")
    result = sum(x * y for x, y in zip(a, b))
    if not math.isfinite(result):
        raise ValueError("dot product must be finite")
    return result


def image_dimensions(data):
    try:
        with Image.open(io.BytesIO(data)) as image:
            if image.format not in ("JPEG", "PNG"):
                raise ValueError("image must be JPEG or PNG")
            return {"width": image.width, "height": image.height}
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("invalid image") from exc


def decode_image(value):
    if not isinstance(value, str):
        raise ValueError("image must be a base64 string")
    try:
        return base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("invalid base64 image") from exc
