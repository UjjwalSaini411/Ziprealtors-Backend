from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EOISubmissionViewSet

router = DefaultRouter()
router.register(r"submissions", EOISubmissionViewSet, basename="eoi-submissions")

urlpatterns = [
    path("", include(router.urls)),
]
