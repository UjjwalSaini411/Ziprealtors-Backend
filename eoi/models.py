from django.db import models

class EOISubmission(models.Model):
    applicant_name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=20)
    email = models.EmailField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant_name} - {self.mobile}"
