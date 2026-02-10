import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EnquirySerializer
from .salesforce import create_enquiry
from .models import Enquiry

logger = logging.getLogger(__name__)

def split_name(full):
    parts = (full or "").strip().split()
    first = parts[0] if parts else ""
    last = " ".join(parts[1:]) if len(parts) > 1 else "Unknown"
    return first, last


class EnquiryView(APIView):
    authentication_classes, permission_classes = [], []

    def post(self, request):
        s = EnquirySerializer(data=request.data)

        if not s.is_valid():
            logger.warning("Enquiry serializer errors: %s", s.errors)
            return Response({"status": "error", "errors": s.errors}, status=400)

        d = s.validated_data

        project_id = (d.get("project_id") or "").strip()
        if not project_id:
            project_id = settings.SF_PROJECT_ID

        # ✅ Save in Django DB
        enquiry_obj = Enquiry.objects.create(
            name=d["name"],
            email=d["email"],
            phone=d["phone"],
            subject=d.get("subject", ""),
            message=d.get("message", ""),
            project_id=project_id
        )

        # ✅ Prepare Salesforce payload
        first, last = split_name(d["name"])
        payload = {
            "enquiryMap": {
                "builderopedia__Status__c": "New",
                "builderopedia__Project__c": project_id,
                "builderopedia__Enquiry_Source__c": "Digital",
                "builderopedia__Enquiry_Sub_Source__c": "Google",
                "builderopedia__Email__c": d["email"],
                "builderopedia__Mobile__c": d["phone"],
                "builderopedia__Subject__c": d.get("subject", ""),
                "builderopedia__Description__c": d.get("message", ""),
            },
            "contactMap": {
                "FirstName": first,
                "LastName": last,
                "PersonEmail": d["email"],
                "PersonMobilePhone": d["phone"],
                "builderopedia__Area_Code_Phone__c": "+91",
            },
            "campaignMap": {"CampaignId": ""},
        }

        try:
            sf = create_enquiry(payload)

            # ✅ Update Django record with Salesforce success
            enquiry_obj.sf_success = True
            enquiry_obj.sf_response = sf
            enquiry_obj.save(update_fields=["sf_success", "sf_response"])

            return Response({
                "status": "success",
                "saved_in_db": True,
                "enquiry_id": enquiry_obj.id,
                "salesforce": sf
            }, status=201)

        except Exception as e:
            logger.exception("Salesforce enquiry failed")

            # ✅ Save error details in DB
            enquiry_obj.sf_success = False
            enquiry_obj.sf_error = str(e)
            enquiry_obj.save(update_fields=["sf_success", "sf_error"])

            return Response({
                "status": "partial_success",
                "saved_in_db": True,
                "enquiry_id": enquiry_obj.id,
                "salesforce_error": str(e) if settings.DEBUG else "Unable to create enquiry in Salesforce"
            }, status=201)
