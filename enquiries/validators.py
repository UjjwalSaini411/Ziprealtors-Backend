import re
from rest_framework import serializers

PHONE_RE = re.compile(r"^[6-9]\d{9}$")

def indian_phone(value: str):
    digits = re.sub(r"\D", "", value or "")
    if not PHONE_RE.match(digits):
        raise serializers.ValidationError("Enter a valid 10-digit Indian mobile.")
    return digits
