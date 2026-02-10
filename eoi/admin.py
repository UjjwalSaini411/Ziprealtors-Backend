from django.contrib import admin
from .models import EOISubmission

@admin.register(EOISubmission)
class EOISubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "applicant_name", "mobile", "email", "created_at")
    list_filter = ("created_at",)
    search_fields = ("applicant_name", "mobile", "email")
    ordering = ("-created_at",)
