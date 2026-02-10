from django.urls import path
from .views import EnquiryView

urlpatterns = [ path("enquiries/", EnquiryView.as_view(), name="enquiries") ]
