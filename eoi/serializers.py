from rest_framework import serializers
from .models import EOISubmission

class EOISubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EOISubmission
        fields = ["id", "applicant_name", "mobile", "email", "created_at"]
        read_only_fields = ["id", "created_at"]
