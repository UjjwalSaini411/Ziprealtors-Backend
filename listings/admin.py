# listings/admin.py
from django.contrib import admin
from .models import Project, PriceItem, ProjectImage
from django.utils.html import format_html

class PriceItemInline(admin.TabularInline):
    model = PriceItem
    extra = 1

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('order', 'type', 'image_file', 'image_url', 'preview',)
    readonly_fields = ('preview',)

    def preview(self, obj):
        url = obj.image
        if url:
            return format_html('<img src="{}" style="max-height:80px; max-width:160px; object-fit:cover;" />', url)
        return "(No image)"
    preview.short_description = "Preview"


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'sector', 'slug', 'developer', 'is_prioritized', 'view_count', 'created_at')
    search_fields = ('name', 'sector', 'developer', 'slug')
    list_filter = ('sector', 'developer', 'is_prioritized')
    list_editable = ('is_prioritized',)  # 👈 checkbox directly editable from list view

    inlines = [PriceItemInline, ProjectImageInline]
    readonly_fields = ('created_at', 'updated_at', 'hero_preview', 'view_count')

    fieldsets = (
        (None, {
            'fields': ('name', 'title', 'external_id', 'slug', 'url', 'sector', 'location', 'developer', 'rera_no', 'rera_link', 'tagline')
        }),
        ('Hero Image', {
            'fields': ('hero_image_file', 'hero_image_url', 'hero_preview'),
        }),
        ('Display Options', {   # 👈 new section
            'fields': ('is_prioritized', 'view_count'),
        }),
        ('Content', {
            'fields': ('description', 'location_info', 'developer_info', 'summary', 'highlights', 'highlights2', 'features')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def hero_preview(self, obj):
        url = obj.hero_image
        if url:
            return format_html('<img src="{}" style="max-height:120px; max-width:280px; object-fit:cover;" />', url)
        return "(No hero image)"
    hero_preview.short_description = "Hero Preview"


@admin.register(PriceItem)
class PriceItemAdmin(admin.ModelAdmin):
    list_display = ('project', 'type', 'area', 'price')

@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ('project', 'type', 'order', 'image_preview', 'image_url')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        url = obj.image
        if url:
            return format_html('<img src="{}" style="max-height:80px; max-width:160px; object-fit:cover;" />', url)
        return "(No image)"
    image_preview.short_description = "Preview"
