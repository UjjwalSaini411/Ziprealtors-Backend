# listings/models.py
from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.db.models import F   # 👈 add this if you'll use F later in model methods
import os


def developer_logo_upload_to(instance, filename):
    slug = instance.slug or slugify(instance.name)[:50]
    return os.path.join('developers', slug, 'logo', filename)

def project_hero_upload_to(instance, filename):
    # e.g., projects/<slug>/hero/<filename>
    slug = instance.slug or slugify(instance.name)[:50]
    return os.path.join('projects', slug, 'hero', filename)

def project_image_upload_to(instance, filename):
    # e.g., projects/<project_slug>/images/<order>-<filename>
    slug = instance.project.slug or slugify(instance.project.name)[:50]
    return os.path.join('projects', slug, 'images', f"{instance.order}-{filename}")


# ─────────────────────────────────────────────────────────
# DEVELOPER MODEL
# ─────────────────────────────────────────────────────────
class Developer(models.Model):
    """Real-estate developer / builder entity."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="SEO-friendly URL key, e.g. 'dlf-limited'",
    )

    # ── Branding ──────────────────────────────────────────
    logo_file = models.ImageField(
        upload_to=developer_logo_upload_to, blank=True, null=True, max_length=500
    )
    logo_url = models.URLField(blank=True, help_text="External logo URL (fallback)")

    # ── Info ──────────────────────────────────────────────
    tagline = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    established_year = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Year developer was founded"
    )
    headquarters = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    rera_developer_id = models.CharField(
        max_length=200, blank=True, help_text="RERA developer registration number"
    )

    # ── Flags ─────────────────────────────────────────────
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this developer prominently on the frontend",
    )

    # ── Rich Content (JSON) ───────────────────────────────
    stats = models.JSONField(blank=True, default=dict, help_text="Metrics e.g. years_of_experience, area_delivered, completed_projects")
    faqs = models.JSONField(blank=True, default=list, help_text="List of dicts: [{'question': '...', 'answer': '...'}]")
    testimonials = models.JSONField(blank=True, default=list, help_text="List of dicts: [{'client': '...', 'feedback': '...', 'rating': 5}]")
    acquisition_method = models.JSONField(blank=True, default=list, help_text="List of dicts: [{'title': '...', 'desc': '...'}]")

    # ── Timestamps ────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'developer'
            slug = base
            i = 1
            while Developer.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def logo(self):
        """Return usable logo URL; prefer uploaded file, then external URL."""
        if self.logo_file:
            try:
                return self.logo_file.url
            except ValueError:
                pass
        return self.logo_url or ""

    @property
    def project_count(self):
        return self.projects.count()


class Project(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=500, blank=True)
    url = models.URLField(blank=True)
    sector = models.CharField(max_length=100, blank=True)
    location = models.TextField(blank=True)
    developer = models.CharField(
        max_length=255, blank=True,
        help_text="Legacy text field — kept for backward compatibility"
    )
    developer_obj = models.ForeignKey(
        'Developer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        help_text="Select from registered developers (preferred over text field)",
    )
    rera_no = models.CharField(max_length=200, blank=True)
    rera_link = models.URLField(blank=True)
    tagline = models.TextField(blank=True)
    hero_image_file = models.ImageField(upload_to=project_hero_upload_to, blank=True, null=True, max_length=500)
    hero_image_url = models.URLField(blank=True)

    description = models.TextField(blank=True)

    highlights = models.JSONField(blank=True, default=list)
    highlights2 = models.JSONField(blank=True, default=list)
    features = models.JSONField(blank=True, default=list)
    summary = models.JSONField(blank=True, default=dict)
    location_info = models.TextField(blank=True)
    developer_info = models.TextField(blank=True)

    # 👇 NEW FIELDS
    is_prioritized = models.BooleanField(
        default=False,
        help_text="Tick to feature this project prominently on the frontend."
    )
    view_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this project page was viewed."
    )

    # ── Property specifics ────────────────────────────────
    STATUS_CHOICES = [
        ('under_construction', 'Under Construction'),
        ('ready_to_move', 'Ready to Move In'),
        ('delivered', 'Delivered'),
    ]
    TYPE_CHOICES = [
        ('residential', 'Residential'),
        ('commercial', 'Commercial'),
        ('sco', 'SCO Plots'),
        ('plots', 'Residential Plots'),
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True)
    property_type = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True)
    project_area = models.CharField(max_length=100, blank=True, help_text="e.g. 5 Acres")
    total_units = models.CharField(max_length=100, blank=True, help_text="e.g. 500 Units")
    towers = models.CharField(max_length=50, blank=True, help_text="e.g. 4 Towers")
    completion_date = models.CharField(max_length=100, blank=True, help_text="e.g. Dec 2025")

    slug = models.SlugField(max_length=255, unique=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    external_id = models.CharField(max_length=255, blank=True, help_text="e.g. id used in front-end JSON")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prioritized projects first, then newest
        ordering = ['-is_prioritized', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or 'project'
            slug = base
            i = 1
            while Project.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def hero_image(self):
        if self.hero_image_file:
            try:
                return self.hero_image_file.url
            except ValueError:
                pass
        return self.hero_image_url or ""


class PriceItem(models.Model):
    project = models.ForeignKey(Project, related_name='price_list', on_delete=models.CASCADE)
    type = models.CharField(max_length=255, blank=True)
    area = models.CharField(max_length=100, blank=True)
    price = models.CharField(max_length=255, blank=True)
    booking_amount = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.type} - {self.area}"

class ProjectImage(models.Model):
    IMAGE_TYPE_CHOICES = [
        ('gallery', 'Gallery'),
        ('masterplan', 'Master Plan'),
        ('map', 'Map'),
        ('network', 'Network'),
        ('project', 'Project'),
        ('all', 'All'),
    ]
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to=project_image_upload_to, blank=True, null=True, max_length=500)
    image_url = models.TextField(blank=True)   # external URL
    type = models.CharField(max_length=50, choices=IMAGE_TYPE_CHOICES, default='gallery')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.name} - {self.type} ({self.order})"

    @property
    def image(self):
        """Return URL for frontend: prefer uploaded file, else fallback to external URL."""
        if self.image_file:
            try:
                return self.image_file.url
            except ValueError:
                pass
        return self.image_url or ""
