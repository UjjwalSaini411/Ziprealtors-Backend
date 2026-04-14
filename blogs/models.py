# blogs/models.py
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import os


def blog_cover_upload_to(instance, filename):
    slug = instance.slug or slugify(instance.title)[:60]
    return os.path.join('blogs', slug, 'cover', filename)


class BlogPost(models.Model):
    CATEGORY_CHOICES = [
        ('market-insights',  'Market Insights'),
        ('buying-guide',     'Buying Guide'),
        ('investment-tips',  'Investment Tips'),
        ('location-guide',   'Location Guide'),
        ('developer-news',   'Developer News'),
    ]

    # ── Core fields ───────────────────────────────────────────────────────────
    title       = models.CharField(max_length=300)
    slug        = models.SlugField(max_length=320, unique=True, blank=True,
                                   help_text="Auto-generated from title. SEO-friendly URL key.")
    excerpt     = models.TextField(
        max_length=400,
        blank=True,
        help_text="Short summary (used as meta description, ~150-160 chars ideal)."
    )
    content     = models.TextField(
        help_text="Full article body in HTML. Use proper H2/H3 heading hierarchy."
    )

    # ── Category & Tags ───────────────────────────────────────────────────────
    category    = models.CharField(max_length=50, choices=CATEGORY_CHOICES,
                                   default='market-insights', db_index=True)
    tags        = models.JSONField(default=list, blank=True,
                                   help_text="List of keyword tags, e.g. ['SCO plots', 'Gurgaon']")

    # ── Cover Image ───────────────────────────────────────────────────────────
    cover_image_file = models.ImageField(
        upload_to=blog_cover_upload_to, blank=True, null=True, max_length=500,
        help_text="Upload a cover image (1200×630 px recommended for OG)."
    )
    cover_image_url  = models.URLField(
        blank=True, help_text="External cover image URL (fallback if no file uploaded)."
    )
    cover_image_alt  = models.CharField(
        max_length=300, blank=True,
        help_text="Alt text for cover image (important for accessibility & SEO)."
    )

    # ── Author ────────────────────────────────────────────────────────────────
    author_name       = models.CharField(max_length=200, default='Zip Realtors LLP')
    author_title      = models.CharField(
        max_length=200, blank=True, default='Real Estate Expert, Gurgaon'
    )
    author_avatar_url = models.URLField(blank=True)

    # ── SEO Overrides ─────────────────────────────────────────────────────────
    meta_title       = models.CharField(
        max_length=120, blank=True,
        help_text="SEO title tag override (leave blank to use article title). Max 60 chars recommended."
    )
    meta_description = models.CharField(
        max_length=320, blank=True,
        help_text="Meta description override (leave blank to use excerpt). Max 160 chars recommended."
    )
    focus_keyword    = models.CharField(
        max_length=200, blank=True,
        help_text="Primary SEO keyword this article targets, e.g. 'SCO plots Gurgaon 2025'."
    )
    canonical_url    = models.URLField(
        blank=True,
        help_text="Canonical URL override (leave blank for auto-canonical)."
    )

    # ── Publication ───────────────────────────────────────────────────────────
    is_published  = models.BooleanField(
        default=False,
        help_text="Tick to make this post publicly visible via the API."
    )
    is_featured   = models.BooleanField(
        default=False,
        help_text="Feature this post prominently on the blog listing page."
    )
    published_at  = models.DateTimeField(
        null=True, blank=True,
        help_text="Set automatically when first published. Can be overridden."
    )

    # ── Auto Stats ────────────────────────────────────────────────────────────
    read_time_minutes = models.PositiveSmallIntegerField(
        default=0,
        help_text="Estimated reading time — auto-computed from word count on save."
    )
    view_count        = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this post detail page was fetched."
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-published_at', '-created_at']
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'

    # ── Save hook ─────────────────────────────────────────────────────────────
    def save(self, *args, **kwargs):
        # Auto-slug
        if not self.slug:
            base = slugify(self.title) or 'blog-post'
            slug = base[:300]
            i = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base[:295]}-{i}"
                i += 1
            self.slug = slug

        # Auto-compute reading time (~200 words per minute)
        word_count = len(self.content.split()) if self.content else 0
        self.read_time_minutes = max(1, round(word_count / 200))

        # Auto set published_at on first publish
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    # ── Properties ────────────────────────────────────────────────────────────
    @property
    def cover_image(self):
        """Return usable cover image URL; prefer uploaded file, then external URL."""
        if self.cover_image_file:
            try:
                return self.cover_image_file.url
            except ValueError:
                pass
        return self.cover_image_url or ""

    @property
    def effective_meta_title(self):
        return self.meta_title or self.title

    @property
    def effective_meta_description(self):
        return self.meta_description or self.excerpt or ""
