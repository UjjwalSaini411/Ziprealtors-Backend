from rest_framework import serializers
from .validators import indian_phone

# SUBJECT_CHOICES = {"buying","selling","renting","investment","other",""}

class EnquirySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15, validators=[indian_phone])
    subject = serializers.CharField(allow_blank=True)
    message = serializers.CharField()
    project_id = serializers.CharField(allow_blank=True, required=False)


    # def validate_subject(self, v):
    #     if v not in SUBJECT_CHOICES:
    #         raise serializers.ValidationError("Invalid subject.")
    #     return v
