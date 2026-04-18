# listings/serializers.py
from rest_framework import serializers
from .models import Project, PriceItem, ProjectImage, Developer


class PriceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceItem
        fields = ['id', 'type', 'area', 'price', 'booking_amount']


class ProjectImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ['id', 'type', 'order', 'image_file', 'image_url', 'image']

    def get_image(self, obj):
        url = obj.image or ""
        request = self.context.get('request')
        if url and url.startswith('/') and request:
            return request.build_absolute_uri(url)
        return url


# ── Developer serializers ──────────────────────────────────────────────────────

class DeveloperListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing / dropdown / header use."""
    logo = serializers.SerializerMethodField()
    project_count = serializers.SerializerMethodField()

    class Meta:
        model = Developer
        fields = [
            'id', 'name', 'slug', 'logo', 'tagline',
            'established_year', 'headquarters', 'website',
            'rera_developer_id', 'is_featured', 'project_count',
        ]

    def get_logo(self, obj):
        url = obj.logo or ""
        request = self.context.get('request')
        if url and url.startswith('/') and request:
            return request.build_absolute_uri(url)
        return url

    def get_project_count(self, obj):
        return obj.project_count


class DeveloperProjectSerializer(serializers.ModelSerializer):
    """Minimal project info embedded inside a developer detail response."""
    hero_image = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'slug', 'name', 'location', 'sector',
            'tagline', 'hero_image', 'is_prioritized', 'view_count',
            'status', 'property_type', 'project_area', 'total_units',
            'towers', 'completion_date',
        ]

    def get_hero_image(self, obj):
        url = obj.hero_image or ""
        request = self.context.get('request')
        if url and url.startswith('/') and request:
            return request.build_absolute_uri(url)
        return url


class DeveloperDetailSerializer(serializers.ModelSerializer):
    """Full developer info including nested projects."""
    logo = serializers.SerializerMethodField()
    project_count = serializers.SerializerMethodField()
    projects = DeveloperProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Developer
        fields = [
            'id', 'name', 'slug', 'logo', 'tagline', 'description',
            'established_year', 'headquarters', 'website',
            'rera_developer_id', 'is_featured',
            'stats', 'faqs', 'testimonials', 'acquisition_method',
            'project_count', 'projects',
            'created_at', 'updated_at',
        ]

    def get_logo(self, obj):
        return obj.logo or ""

    def get_project_count(self, obj):
        return obj.project_count


# ── Project serializer ─────────────────────────────────────────────────────────

class ProjectSerializer(serializers.ModelSerializer):
    price_list = PriceItemSerializer(many=True, read_only=True)
    images = ProjectImageSerializer(many=True, read_only=True)
    hero_image = serializers.SerializerMethodField()
    developer_slug = serializers.SerializerMethodField()
    developer_name = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'external_id', 'name', 'title', 'url', 'slug',
            'sector', 'location',
            'developer', 'developer_slug', 'developer_name',
            'rera_no', 'rera_link', 'tagline',
            'hero_image', 'hero_image_file', 'hero_image_url',
            'description', 'summary', 'location_info', 'developer_info',
            'highlights', 'highlights2', 'features',
            'is_prioritized', 'view_count',
            'status', 'property_type', 'project_area', 'total_units',
            'towers', 'completion_date',
            'price_list', 'images',
            'created_at', 'updated_at',
        ]

    def get_hero_image(self, obj):
        url = obj.hero_image or ""
        request = self.context.get('request')
        if url and url.startswith('/') and request:
            return request.build_absolute_uri(url)
        return url

    def get_developer_slug(self, obj):
        if obj.developer_obj:
            return obj.developer_obj.slug
        return ""

    def get_developer_name(self, obj):
        if obj.developer_obj:
            return obj.developer_obj.name
        return obj.developer or ""
