# listings/urls.py
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, DeveloperViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'developers', DeveloperViewSet, basename='developer')

urlpatterns = [
    path('', include(router.urls)),
]
