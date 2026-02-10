import os
from django.conf import settings
from django.core.mail import EmailMessage

def send_eoi_email(applicant_name, recipient_email):
    subject = "Expression of Interest Received – Action Required"
    body = f"""
Hi {applicant_name},

Thank you for submitting your Expression of Interest.

Please find attached the required PDF documents.

📌 Action Required:
1. Save the attached form to your device.
2. Fill in the form completely.
3. Reply to this same email with the filled form attached.

Once we receive your completed form, we will proceed with the next steps.

Regards,
Team MintGinger
"""

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )

    # Attach PDFs
    pdf1_path = os.path.join(settings.MEDIA_ROOT, "pdfs", "dp.pdf")
    pdf2_path = os.path.join(settings.MEDIA_ROOT, "pdfs", "form.pdf")

    if os.path.exists(pdf1_path):
        email.attach_file(pdf1_path)

    if os.path.exists(pdf2_path):
        email.attach_file(pdf2_path)

    email.send(fail_silently=False)
