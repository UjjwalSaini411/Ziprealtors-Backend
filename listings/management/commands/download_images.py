"""
listings/management/commands/download_images.py

Downloads all external hero images and project gallery images from
image_url / hero_image_url fields and saves them into the local
media/ directory via the proper ImageField.

Usage:
    python manage.py download_images
    python manage.py download_images --dry-run       # just print, don't save
    python manage.py download_images --skip-existing # skip already-downloaded ones
    python manage.py download_images --workers 4     # parallel downloads (default 4)
"""

import os
import time
import threading
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from typing import Optional

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db import transaction

from listings.models import Project, ProjectImage


# ── helpers ────────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
}

_print_lock = threading.Lock()


def _log(style_fn, msg):
    with _print_lock:
        print(style_fn(msg))


def _fetch_url(url: str, timeout: int = 30) -> Optional[bytes]:
    """Download bytes from a URL, return None on error."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception as e:
        return None


def _ext_from_url(url: str, default: str = ".jpg") -> str:
    """Guess file extension from URL path or MIME type."""
    path = url.split("?")[0]
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"):
        return ext
    return default


def _filename_from_url(url: str) -> str:
    """Build a safe filename from the last URL path segment."""
    part = url.rstrip("/").split("/")[-1].split("?")[0]
    part = part[:80] or "image"
    _, ext = os.path.splitext(part)
    if ext.lower() not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        part = part + ".jpg"
    return part


# ── task functions ─────────────────────────────────────────────────────────────

def _download_hero(project: Project, dry_run: bool, skip_existing: bool) -> str:
    """Download hero_image_url and save to hero_image_file. Returns status string."""
    url = project.hero_image_url
    if not url:
        return f"[skip-no-url] Project #{project.id} {project.name!r}"

    if not url.startswith("http://") and not url.startswith("https://"):
        return f"[skip-invalid] Project #{project.id} URL: {url}"

    if skip_existing and project.hero_image_file:
        return f"[exists]      Project #{project.id} {project.name!r}"

    if dry_run:
        return f"[dry-run]     Project #{project.id} hero -> {url}"

    data = _fetch_url(url)
    if not data:
        return f"[FAIL]        Project #{project.id} hero URL: {url}"

    filename = _filename_from_url(url)
    with transaction.atomic():
        project.refresh_from_db()
        project.hero_image_file.save(filename, ContentFile(data), save=False)
        # Clear the URL field since we now serve from file
        project.hero_image_url = ""
        project.save(update_fields=["hero_image_file", "hero_image_url"])

    return f"[OK-hero]     Project #{project.id} {project.name!r} saved as {filename}"


def _download_project_image(img: ProjectImage, dry_run: bool, skip_existing: bool) -> str:
    """Download image_url and save to image_file. Returns status string."""
    url = img.image_url
    if not url:
        return f"[skip-no-url] Image #{img.id}"

    # Handle cases where url is a stringified dictionary like "{'type': 'img', 'src': 'http...'}"
    if url.startswith("{") and "'src':" in url:
        import ast
        try:
            parsed = ast.literal_eval(url)
            if isinstance(parsed, dict) and 'src' in parsed:
                url = parsed['src']
        except Exception:
            pass

    # Skip relative URLs or invalid protocols
    if not url.startswith("http://") and not url.startswith("https://"):
        return f"[skip-invalid] Image #{img.id} URL: {url}"

    if skip_existing and img.image_file:
        return f"[exists]      Image #{img.id}"

    if dry_run:
        return f"[dry-run]     Image #{img.id} ({img.type}) -> {url}"

    data = _fetch_url(url)
    if not data:
        return f"[FAIL]        Image #{img.id} URL: {url}"

    filename = _filename_from_url(url)
    with transaction.atomic():
        img.refresh_from_db()
        img.image_file.save(filename, ContentFile(data), save=False)
        img.image_url = ""
        img.save(update_fields=["image_file", "image_url"])

    return f"[OK-img]      Image #{img.id} project={img.project_id} type={img.type} saved as {filename}"


# ── command ────────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = (
        "Download all external images (hero_image_url + image_url) into local "
        "media storage and update the corresponding ImageFields."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print what would be downloaded without saving anything.",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            default=True,
            help="Skip records that already have a local image_file (default: True).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Re-download all images even if image_file is already set (overrides --skip-existing).",
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=4,
            help="Number of parallel download threads (default: 4).",
        )
        parser.add_argument(
            "--heroes-only",
            action="store_true",
            default=False,
            help="Only download hero images, skip gallery images.",
        )
        parser.add_argument(
            "--gallery-only",
            action="store_true",
            default=False,
            help="Only download gallery/project images, skip hero images.",
        )

    def handle(self, *args, **options):
        dry_run      = options["dry_run"]
        force        = options["force"]
        skip_existing = not force  # --force overrides --skip-existing
        workers      = options["workers"]
        heroes_only  = options["heroes_only"]
        gallery_only = options["gallery_only"]

        t_start = time.time()
        ok = fail = skipped = 0

        tasks = []

        # ── Hero images ────────────────────────────────────────────────────────
        if not gallery_only:
            heroes = Project.objects.exclude(hero_image_url="").exclude(hero_image_url__isnull=True)
            self.stdout.write(f"Found {heroes.count()} projects with hero_image_url")
            for proj in heroes.iterator():
                tasks.append(("hero", proj))

        # ── Gallery / project images ───────────────────────────────────────────
        if not heroes_only:
            imgs = ProjectImage.objects.exclude(image_url="").exclude(image_url__isnull=True)
            self.stdout.write(f"Found {imgs.count()} project images with image_url")
            for img in imgs.iterator():
                tasks.append(("img", img))

        total = len(tasks)
        self.stdout.write(f"\nStarting download of {total} assets with {workers} workers...\n")

        # ── Linear download (safe for SQLite) ──────────────────────────────────
        done = 0
        for kind, obj in tasks:
            if kind == "hero":
                result = _download_hero(obj, dry_run, skip_existing)
            else:
                result = _download_project_image(obj, dry_run, skip_existing)
            
            done += 1
            tag = result.split("]")[0].strip("[").strip()
            if tag.startswith("OK"):
                ok += 1
                self.stdout.write(self.style.SUCCESS(result))
            elif tag == "FAIL":
                fail += 1
                self.stdout.write(self.style.ERROR(result))
            elif tag.startswith("exists") or tag.startswith("skip"):
                skipped += 1
                self.stdout.write(self.style.WARNING(result))
            else:
                self.stdout.write(result)

            if done % 25 == 0:
                self.stdout.write(f"  [{done}/{total} done]")

        elapsed = time.time() - t_start
        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone in {elapsed:.1f}s -- "
                f"{ok} downloaded, {skipped} skipped, {fail} failed out of {total} total."
            )
        )
