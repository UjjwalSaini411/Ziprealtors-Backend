# listings/views.py
from rest_framework import viewsets, filters
from django.db.models import F
from .models import Project, Developer
from .serializers import ProjectSerializer, DeveloperListSerializer, DeveloperDetailSerializer
from rest_framework.response import Response


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all().prefetch_related('price_list', 'images', 'developer_obj')
    serializer_class = ProjectSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sector', 'location', 'developer']
    ordering_fields = ['created_at', 'name', 'sector', 'is_prioritized', 'view_count']
    ordering = ['-is_prioritized', '-created_at']

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view_count atomically
        Project.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.refresh_from_db(fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class DeveloperViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/developers/          → list  (DeveloperListSerializer)
    /api/developers/<slug>/   → detail (DeveloperDetailSerializer)
    SEO-friendly slugs, e.g. /api/developers/dlf-limited/
    """
    queryset = Developer.objects.prefetch_related('projects')
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'headquarters', 'rera_developer_id']
    ordering_fields = ['name', 'established_year', 'is_featured']
    ordering = ['-is_featured', 'name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DeveloperDetailSerializer
        return DeveloperListSerializer
