import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EnquirySerializer
from .models import Enquiry

logger = logging.getLogger(__name__)

class EnquiryView(APIView):
    authentication_classes, permission_classes = [], []

    def post(self, request):
        s = EnquirySerializer(data=request.data)

        if not s.is_valid():
            logger.warning("Enquiry serializer errors: %s", s.errors)
            return Response({"status": "error", "errors": s.errors}, status=400)

        d = s.validated_data

        project_id = (d.get("project_id") or "").strip()

        # ✅ Save in Django DB
        enquiry_obj = Enquiry.objects.create(
            name=d["name"],
            email=d["email"],
            phone=d["phone"],
            subject=d.get("subject", ""),
            message=d.get("message", ""),
            project_id=project_id
        )

        return Response({
            "status": "success",
            "saved_in_db": True,
            "enquiry_id": enquiry_obj.id,
        }, status=201)
