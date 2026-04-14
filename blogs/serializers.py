# blogs/serializers.py
from rest_framework import serializers
from .models import BlogPost


class BlogListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for blog listing page."""
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'slug', 'title', 'excerpt',
            'cover_image', 'cover_image_alt',
            'category', 'tags',
            'author_name', 'author_title', 'author_avatar_url',
            'read_time_minutes', 'is_featured',
            'published_at', 'view_count',
        ]

    def get_cover_image(self, obj):
        url = obj.cover_image or ""
        request = self.context.get('request')
        if url and url.startswith('/') and request:
            return request.build_absolute_uri(url)
        return url


class BlogDetailSerializer(serializers.ModelSerializer):
    """Full serializer for blog detail page — includes content + SEO fields."""
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'slug', 'title', 'excerpt', 'content',
            'cover_image', 'cover_image_alt',
            'category', 'tags',
            'author_name', 'author_title', 'author_avatar_url',
            'meta_title', 'meta_description', 'focus_keyword', 'canonical_url',
            'read_time_minutes', 'is_featured',
            'published_at', 'created_at', 'updated_at', 'view_count',
        ]

    def get_cover_image(self, obj):
        url = obj.cover_image or ""
        request = self.context.get('request')
        if url and url.startswith('/') and request:
            return request.build_absolute_uri(url)
        return url
