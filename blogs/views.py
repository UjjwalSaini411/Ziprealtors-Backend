# blogs/views.py
from rest_framework import viewsets, filters
from rest_framework.response import Response
from django.db.models import F
from .models import BlogPost
from .serializers import BlogListSerializer, BlogDetailSerializer


class BlogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/blogs/          → list  (BlogListSerializer)
    /api/blogs/<slug>/   → detail (BlogDetailSerializer, increments view_count)

    Query params supported on list:
      ?category=buying-guide
      ?featured=true
      ?search=SCO
      ?ordering=-published_at (default)
    """
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'excerpt', 'content', 'focus_keyword', 'tags', 'author_name']
    ordering_fields = ['published_at', 'created_at', 'view_count', 'read_time_minutes']
    ordering = ['-is_featured', '-published_at']

    def get_queryset(self):
        qs = BlogPost.objects.filter(is_published=True)

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)

        # Filter featured only
        featured = self.request.query_params.get('featured', '').lower()
        if featured in ('true', '1', 'yes'):
            qs = qs.filter(is_featured=True)

        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogDetailSerializer
        return BlogListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view_count atomically (same pattern as ProjectViewSet)
        BlogPost.objects.filter(pk=instance.pk).update(view_count=F('view_count') + 1)
        instance.refresh_from_db(fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
