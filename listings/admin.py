# listings/admin.py
from django.contrib import admin
from .models import Project, PriceItem, ProjectImage, Developer
from django.utils.html import format_html


# ── Developer Admin ────────────────────────────────────────────────────────────

@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'established_year', 'headquarters', 'is_featured', 'project_count_display', 'created_at')
    search_fields = ('name', 'slug', 'headquarters', 'rera_developer_id')
    list_filter = ('is_featured',)
    list_editable = ('is_featured',)
    readonly_fields = ('slug', 'created_at', 'updated_at', 'logo_preview', 'project_count_display')
    prepopulated_fields = {}  # slug is auto-generated on save

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'tagline', 'is_featured'),
        }),
        ('Logo', {
            'fields': ('logo_file', 'logo_url', 'logo_preview'),
        }),
        ('Details', {
            'fields': ('description', 'established_year', 'headquarters', 'website', 'rera_developer_id'),
        }),
        ('Stats', {
            'fields': ('project_count_display',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def logo_preview(self, obj):
        url = obj.logo
        if url:
            return format_html('<img src="{}" style="max-height:80px; max-width:200px; object-fit:contain;" />', url)
        return "(No logo)"
    logo_preview.short_description = "Logo Preview"

    def project_count_display(self, obj):
        return obj.project_count
    project_count_display.short_description = "# Projects"


# ── Project Inlines ────────────────────────────────────────────────────────────

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


# ── Project Admin ──────────────────────────────────────────────────────────────

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'sector', 'slug', 'developer_display', 'is_prioritized', 'view_count', 'created_at')
    search_fields = ('name', 'sector', 'developer', 'slug')
    list_filter = ('sector', 'is_prioritized', 'developer_obj')
    list_editable = ('is_prioritized',)

    inlines = [PriceItemInline, ProjectImageInline]
    readonly_fields = ('created_at', 'updated_at', 'hero_preview', 'view_count')
    autocomplete_fields = ['developer_obj']  # gives a nice search widget

    fieldsets = (
        (None, {
            'fields': (
                'name', 'title', 'external_id', 'slug', 'url',
                'sector', 'location',
                'developer_obj',   # ← FK dropdown (preferred)
                'developer',       # ← legacy text (kept for backward compat)
                'rera_no', 'rera_link', 'tagline',
            )
        }),
        ('Hero Image', {
            'fields': ('hero_image_file', 'hero_image_url', 'hero_preview'),
        }),
        ('Display Options', {
            'fields': ('is_prioritized', 'view_count'),
        }),
        ('Content', {
            'fields': ('description', 'location_info', 'developer_info', 'summary', 'highlights', 'highlights2', 'features')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def developer_display(self, obj):
        if obj.developer_obj:
            return obj.developer_obj.name
        return obj.developer or "—"
    developer_display.short_description = "Developer"

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
