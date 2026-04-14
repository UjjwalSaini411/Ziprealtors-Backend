# blogs/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display  = (
        'title', 'category', 'author_name',
        'is_published', 'is_featured',
        'read_time_minutes', 'view_count', 'published_at',
    )
    list_filter   = ('category', 'is_published', 'is_featured')
    list_editable = ('is_published', 'is_featured')
    search_fields = ('title', 'excerpt', 'content', 'focus_keyword', 'author_name')
    readonly_fields = (
        'slug', 'read_time_minutes', 'view_count',
        'cover_preview', 'created_at', 'updated_at',
    )
    prepopulated_fields = {}  # slug auto-generated on save
    date_hierarchy  = 'published_at'
    ordering        = ('-is_featured', '-published_at', '-created_at')

    fieldsets = (
        ('📝 Basic Info', {
            'fields': (
                'title', 'slug',
                'excerpt', 'content',
                'category', 'tags',
            ),
        }),
        ('🖼️ Cover Image', {
            'fields': ('cover_image_file', 'cover_image_url', 'cover_image_alt', 'cover_preview'),
        }),
        ('✍️ Author', {
            'fields': ('author_name', 'author_title', 'author_avatar_url'),
        }),
        ('🔍 SEO Fields', {
            'classes': ('collapse',),
            'fields': (
                'focus_keyword',
                'meta_title',
                'meta_description',
                'canonical_url',
            ),
            'description': (
                'Leave blank to auto-derive from title/excerpt. '
                'meta_title max 60 chars, meta_description max 160 chars.'
            ),
        }),
        ('🚀 Publication', {
            'fields': ('is_published', 'is_featured', 'published_at'),
        }),
        ('📊 Stats (read-only)', {
            'fields': ('read_time_minutes', 'view_count', 'created_at', 'updated_at'),
        }),
    )

    actions = ['publish_selected', 'unpublish_selected', 'feature_selected']

    # ── Custom admin actions ────────────────────────────────────────────────

    def publish_selected(self, request, queryset):
        updated = queryset.filter(is_published=False).update(
            is_published=True, published_at=timezone.now()
        )
        self.message_user(request, f"✅ {updated} post(s) published.")
    publish_selected.short_description = "✅ Publish selected posts"

    def unpublish_selected(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"🔒 {updated} post(s) unpublished.")
    unpublish_selected.short_description = "🔒 Unpublish selected posts"

    def feature_selected(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"⭐ {updated} post(s) marked as featured.")
    feature_selected.short_description = "⭐ Mark selected posts as featured"

    # ── Cover preview ───────────────────────────────────────────────────────

    def cover_preview(self, obj):
        url = obj.cover_image
        if url:
            return format_html(
                '<img src="{}" style="max-height:120px; max-width:280px; '
                'object-fit:cover; border-radius:4px;" />',
                url,
            )
        return "(No cover image)"
    cover_preview.short_description = "Cover Preview"
