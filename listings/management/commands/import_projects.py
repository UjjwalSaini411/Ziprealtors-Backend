import json
import re
import ast
from django.core.management.base import BaseCommand, CommandError
from listings.models import Project, PriceItem, ProjectImage
from django.db import transaction

def try_parse_json_file(path):
    """
    Try multiple strategies to parse a file that *should* contain a JSON array
    of project objects. Handles:
      - pure JSON
      - JavaScript module like: export const projects = [ ... ];
      - a file containing an array anywhere (extracts first [ ... ])
      - fallback to ast.literal_eval (works for Python-like dicts using single quotes)
    Returns a Python object (usually list).
    Raises ValueError on failure.
    """
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    # 1) Try pure JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2) Try extracting the first [...] substring (handles export const projects = [...] etc)
    arr_match = re.search(r'(\[.*\])', text, flags=re.S)
    if arr_match:
        arr_text = arr_match.group(1)
        try:
            return json.loads(arr_text)
        except json.JSONDecodeError:
            # 3) Try to be tolerant: replace single quotes with double quotes (best-effort)
            try:
                normalized = arr_text.replace("'", '"')
                return json.loads(normalized)
            except json.JSONDecodeError:
                pass

    # 4) Final fallback: try ast.literal_eval (accepts Python dict/list syntax)
    try:
        return ast.literal_eval(text)
    except Exception:
        # Try literal eval on array substring if we found it
        if arr_match:
            try:
                return ast.literal_eval(arr_text)
            except Exception:
                pass

    raise ValueError("Failed to parse file as JSON/JS/Python-like array. Ensure the file contains a JSON array (or JS file with an array) and pass its path.")

class Command(BaseCommand):
    help = "Import projects JSON into DB. Usage: python manage.py import_projects path/to/projects.json"

    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str)

    def handle(self, *args, **options):
        path = options['json_path']
        try:
            data = try_parse_json_file(path)
        except ValueError as e:
            raise CommandError(f"Could not parse input file: {e}")

        # If file contains an object with key like { projects: [...] } or { "projects": [...] }
        if isinstance(data, dict):
            # prefer keys that look like 'projects' or 'data'
            if 'projects' in data and isinstance(data['projects'], (list, tuple)):
                data = data['projects']
            elif 'data' in data and isinstance(data['data'], (list, tuple)):
                data = data['data']
            else:
                # maybe it's a single project object - convert to list
                data = [data]

        if not isinstance(data, (list, tuple)):
            raise CommandError("Parsed content is not a list/array. Make sure the file contains an array of project objects.")

        # quick sanity check: ensure items are dicts or convertible
        bad_items = [i for i in data if not isinstance(i, dict)]
        if bad_items:
            # Try to decode items that are JSON strings inside list (rare); attempt json.loads each string
            transformed = []
            could_transform = True
            for item in data:
                if isinstance(item, dict):
                    transformed.append(item)
                elif isinstance(item, str):
                    try:
                        transformed.append(json.loads(item))
                    except Exception:
                        could_transform = False
                        break
                else:
                    could_transform = False
                    break
            if could_transform:
                data = transformed
            else:
                raise CommandError("Some items in the top-level array are not objects (dict). Please pass a JSON array of objects or a JS file that contains an array of objects.")

        # Now import each project dict
        for item in data:
            # defensive: item must be dict now
            if not isinstance(item, dict):
                # skip if somehow still not dict
                self.stdout.write(self.style.WARNING("Skipping unexpected non-object item."))
                continue

            name = item.get('name') or item.get('title') or 'Unnamed'
            with transaction.atomic():
                p, created_flag = Project.objects.get_or_create(
                    external_id=item.get('id',''),
                    defaults={
                        'name': name[:255],
                        'title': item.get('title',''),
                        'url': item.get('url',''),
                        'sector': item.get('sector',''),
                        'location': item.get('location',''),
                        'developer': item.get('developer',''),
                        'rera_no': item.get('reraNo',''),
                        'rera_link': item.get('reraLink',''),
                        'tagline': item.get('tagline',''),
                        # populate hero_image_url from JSON heroImage if present
                        'hero_image_url': item.get('heroImage',''),
                        'description': item.get('description',''),
                        'highlights': item.get('highlights',[]),
                        'highlights2': item.get('highlights2',[]),
                        'features': item.get('features',[]),
                        'summary': item.get('summary',{}),
                        'location_info': item.get('locationInfo',''),
                        'developer_info': item.get('developerInfo',''),
                    }
                )

                if not created_flag:
                    # update fields when project already exists
                    p.title = item.get('title','')
                    p.url = item.get('url','')
                    p.sector = item.get('sector','')
                    p.location = item.get('location','')
                    p.developer = item.get('developer','')
                    p.rera_no = item.get('reraNo','')
                    p.rera_link = item.get('reraLink','')
                    p.tagline = item.get('tagline','')
                    p.hero_image_url = item.get('heroImage','')
                    p.description = item.get('description','')
                    p.highlights = item.get('highlights',[])
                    p.highlights2 = item.get('highlights2',[])
                    p.features = item.get('features',[])
                    p.summary = item.get('summary',{})
                    p.location_info = item.get('locationInfo','')
                    p.developer_info = item.get('developerInfo','')
                    p.save()

                # recreate price items and images (simple)
                PriceItem.objects.filter(project=p).delete()
                for pl in item.get('priceList',[]):
                    PriceItem.objects.create(
                        project=p,
                        type=pl.get('type',''),
                        area=pl.get('area',''),
                        price=pl.get('price',''),
                        booking_amount=pl.get('bookingAmount','')
                    )

                ProjectImage.objects.filter(project=p).delete()
                images = item.get('images', {})
                # handle common keys - gallery/masterPlan/map/network/project/all
                key_mapping = {
                    'gallery': 'gallery',
                    'masterPlan': 'masterplan',
                    'map': 'map',
                    'network': 'network',
                    'project': 'project',
                    'all': 'all',
                }
                for key, type_name in key_mapping.items():
                    arr = images.get(key, [])
                    if isinstance(arr, list):
                        for i, url in enumerate(arr):
                            if url:
                                ProjectImage.objects.create(project=p, image_url=url, type=type_name, order=i)

        self.stdout.write(self.style.SUCCESS("Import complete"))
