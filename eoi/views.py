from rest_framework import viewsets
from .models import EOISubmission
from .serializers import EOISubmissionSerializer
from .utils import send_eoi_email

class EOISubmissionViewSet(viewsets.ModelViewSet):
    queryset = EOISubmission.objects.all().order_by("-created_at")
    serializer_class = EOISubmissionSerializer

    def perform_create(self, serializer):
        submission = serializer.save()

        # send email to applicant
        send_eoi_email(submission.applicant_name, submission.email)
