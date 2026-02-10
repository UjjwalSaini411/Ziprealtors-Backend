from django.db import models

class Enquiry(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField(blank=True)
    project_id = models.CharField(max_length=100, blank=True)

    # Salesforce tracking
    sf_success = models.BooleanField(default=False)
    sf_response = models.JSONField(null=True, blank=True)
    sf_error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"
