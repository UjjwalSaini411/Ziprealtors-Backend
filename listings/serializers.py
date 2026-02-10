# listings/serializers.py
from rest_framework import serializers
from .models import Project, PriceItem, ProjectImage

class PriceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceItem
        fields = ['id','type','area','price','booking_amount']

class ProjectImageSerializer(serializers.ModelSerializer):
    # expose image as computed field (prefers uploaded file URL)
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ['id','type','order','image_file','image_url','image']

    def get_image(self, obj):
        # returns final usable URL (or empty string)
        return obj.image or ""

# listings/serializers.py
class ProjectSerializer(serializers.ModelSerializer):
    price_list = PriceItemSerializer(many=True, read_only=True)
    images = ProjectImageSerializer(many=True, read_only=True)
    hero_image = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id','external_id','name','title','url','slug','sector','location','developer','rera_no','rera_link','tagline',
            'hero_image', 'hero_image_file', 'hero_image_url',
            'description','summary','location_info','developer_info',
            'highlights','highlights2','features',
            'is_prioritized', 'view_count',      # 👈 NEW
            'price_list','images','created_at','updated_at'
        ]

    def get_hero_image(self, obj):
        return obj.hero_image or ""

