# blogs/urls.py
from rest_framework.routers import DefaultRouter
from .views import BlogViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'blogs', BlogViewSet, basename='blog')

urlpatterns = [
    path('', include(router.urls)),
]
