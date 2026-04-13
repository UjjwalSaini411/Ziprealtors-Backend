import sys
from django.core.management.base import BaseCommand
from django.db import transaction
from listings.models import Project, Developer

KNOWN_DEVELOPERS = [
    "DLF", "Godrej", "M3M", "Vatika", "Bestech", "Emaar", 
    "Signature Global", "Signature", "Tata", "Puri", "Sobha", "ATS", 
    "Krisumi", "Whiteland", "Eldeco", "Conscient", "Paras", 
    "Orris", "Microtek", "Spaze", "Mahindra", "Indiabulls",
    "Smartworld", "Smart World", "Experion", "Raheja", "SS Group", "Adani", 
    "WTC", "Wal Group", "Pyramid", "County", "Imperia", "Capital One",
    "Hero", "Omaxe", "Central Park", "Ashiana", "Elan",
    "Kashish", "M2K", "Oxirich", "Landmark", "AIPL", "BPTP", "Joyville", 
    "JMS", "Assotech", "Ansal", "Sare", "Vardhman", "Lotus", "India",
    "Ganga", "Alpha", "Parkview", "Vipul", "Mapsko", "Umang", "Max"
]

class Command(BaseCommand):
    help = "Intelligently extracts developers from project names when developer field is empty."

    def handle(self, *args, **options):
        projects = Project.objects.filter(developer_obj__isnull=True)
        self.stdout.write(f"Found {projects.count()} projects missing a developer mapping.")
        
        dev_cache = {d.name.lower(): d for d in Developer.objects.all()}
        
        # Add basic aliases for matching
        aliases = {}
        for d in dev_cache.values():
            base_name = d.name.lower().replace(' group', '').replace(' limited', '').replace(' developers', '').replace(' infrastructure', '').replace(' corporation', '')
            aliases[base_name] = d

        updated = 0
        newly_created = 0

        with transaction.atomic():
            for project in projects:
                name_lower = project.name.lower()
                matched_dev = None

                # 1. Try to match an existing developer
                for alias_name, dev in aliases.items():
                    if name_lower.startswith(alias_name):
                        matched_dev = dev
                        break
                
                # 2. Try against the KNOWN_DEVELOPERS list if no existing match
                if not matched_dev:
                    for kd in KNOWN_DEVELOPERS:
                        if name_lower.startswith(kd.lower()):
                            # Create or retrieve it
                            new_name = kd + " Group" if kd not in ["Signature Global", "DLF", "Godrej", "M3M", "Tata"] else kd
                            
                            # check cache again
                            lookup = new_name.lower().replace(' group', '')
                            if lookup in aliases:
                                matched_dev = aliases[lookup]
                            else:
                                matched_dev, created = Developer.objects.get_or_create(name=new_name)
                                if created:
                                    matched_dev.save()
                                    newly_created += 1
                                dev_cache[matched_dev.name.lower()] = matched_dev
                                aliases[lookup] = matched_dev
                            break

                # 3. Update the project
                if matched_dev:
                    project.developer_obj = matched_dev
                    project.developer = matched_dev.name # Also update the legacy string
                    project.save(update_fields=['developer_obj', 'developer'])
                    updated += 1
                else:
                    self.stdout.write(self.style.WARNING(f"Could not automatically determine developer for: {project.name}"))

        self.stdout.write(self.style.SUCCESS(f"Finished! Created {newly_created} new developers and matched {updated} to projects."))
