from django.contrib import admin
from .models import Enquiry

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "email", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name", "phone", "email")
    ordering = ("-created_at",)
