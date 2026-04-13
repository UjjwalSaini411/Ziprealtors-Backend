import sys
from django.core.management.base import BaseCommand
from django.db import transaction
from listings.models import Project, Developer

class Command(BaseCommand):
    help = "Extracts developer names from Projects, creates Developer records, and updates Projects with the developer_obj foreign key."

    def handle(self, *args, **options):
        projects = Project.objects.all()
        created_count = 0
        updated_count = 0
        
        # Track developers to avoid hitting DB too many times for info
        dev_cache = {}

        self.stdout.write(f"Starting developer population. Total projects: {projects.count()}")

        with transaction.atomic():
            for project in projects:
                dev_name = (project.developer or "").strip()
                
                # If there's no developer name, skip
                if not dev_name:
                    continue

                if dev_name not in dev_cache:
                    # Get or create the Developer
                    # Initialize with any available developer_info from the project (if not already set)
                    dev_info = (project.developer_info or "").strip()
                    defaults = {}
                    if dev_info:
                        defaults['description'] = dev_info[:1000]  # Just take some text as description
                        
                    dev, created = Developer.objects.get_or_create(
                        name=dev_name,
                        defaults=defaults
                    )
                    
                    if created:
                        created_count += 1
                        # Save it again to trigger the slugify hook just in case
                        dev.save()
                    
                    dev_cache[dev_name] = dev

                dev_obj = dev_cache[dev_name]

                # Update the project's foreign key if it's not set or incorrect
                if project.developer_obj_id != dev_obj.id:
                    project.developer_obj = dev_obj
                    project.save(update_fields=['developer_obj'])
                    updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} developers and updated {updated_count} projects."))
