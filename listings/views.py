# listings/views.py
from rest_framework import viewsets, filters
from django.db.models import F
from .models import Project
from .serializers import ProjectSerializer
from rest_framework.response import Response


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Project.objects.all().prefetch_related('price_list', 'images')
    serializer_class = ProjectSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'sector', 'location', 'developer']
    ordering_fields = ['created_at', 'name', 'sector', 'is_prioritized', 'view_count']
    ordering = ['-is_prioritized', '-created_at']  # 👈 prioritized first, newest first

    def retrieve(self, request, *args, **kwargs):
        # Get instance normally
        instance = self.get_object()

        # Increment view_count atomically
        Project.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)

        # Refresh instance so serializer shows updated value
        instance.refresh_from_db(fields=['view_count'])

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
