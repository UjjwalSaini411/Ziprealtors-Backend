from django.core.management.base import BaseCommand
from listings.models import Developer, Project
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Seeds rich data for developers and projects to showcase the new layouts.'

    def handle(self, *args, **options):
        # 1. Seed Developer (DLF Properties)
        dlf, created = Developer.objects.get_or_create(
            name="DLF Limited",
            defaults={
                "slug": "dlf-limited",
            }
        )
        dlf.tagline = "The Asset That Serves Your Heart & Your Portfolio"
        dlf.headquarters = "Gurugram, Haryana"
        dlf.established_year = 1946
        dlf.website = "https://www.dlf.in"
        dlf.rera_developer_id = "REP/HAR/123/2017"
        dlf.is_featured = True
        dlf.description = "With 78+ years of real estate investment, development, and management experience, DLF has an unparalleled scale of delivery and an unmatched track record of customer-centric service excellence in India."
        dlf.stats = {
            "years_of_experience": "78+",
            "area_delivered": "32.63 Cr sqft",
            "completed_projects": "112",
            "ongoing_projects_area": "17.84 million sqft",
            "large_resident_base": "1 million+"
        }
        dlf.faqs = [
            {"question": "Why invest in DLF properties?", "answer": "DLF offers high market appreciation, unmatched quality, and luxury status."},
            {"question": "Are DLF projects RERA registered?", "answer": "Yes, all our ongoing projects comply with RERA guidelines."},
            {"question": "What payment plans are offered?", "answer": "We offer construction-linked, down-payment, and special schemes."},
            {"question": "Can I book a site visit through you?", "answer": "Yes, contact our channel partner Zip Realtors for a free visit."},
        ]
        dlf.testimonials = [
            {"client": "Rebecca Kantor", "feedback": "Wonderful stress-free and painless site-unseen-house-purchase experience. Thanks to the team for the regular updates and transparency.", "rating": 5},
            {"client": "Arjun Singh", "feedback": "Timely delivery and premium quality construction as always.", "rating": 5}
        ]
        dlf.acquisition_method = [
            {"title": "Goal Analysis", "desc": "Mapping investment goals to ensure we align perfectly with your vision."},
            {"title": "Strategic Shortlisting", "desc": "Narrowing down based on ROI, location, and budget."},
            {"title": "Financial Optimization", "desc": "Structuring payment plans for maximum yield."},
            {"title": "Smooth Execution", "desc": "Seamless paperwork and delivery handover."}
        ]
        dlf.save()

        # Seed Projects for DLF
        projects_data = [
            {
                "name": "DLF Camellias",
                "sector": "Sector 42",
                "location": "Golf Course Road, Gurugram",
                "tagline": "Ultra Luxury Residences",
                "status": "ready_to_move",
                "property_type": "residential",
                "project_area": "17.5 Acres",
                "total_units": "429 Units",
                "towers": "9 Towers",
                "completion_date": "Delivered",
                "is_prioritized": True,
            },
            {
                "name": "DLF Privana South",
                "sector": "Sector 76",
                "location": "SPR Road, Gurugram",
                "tagline": "Nature Integrated Living",
                "status": "under_construction",
                "property_type": "residential",
                "project_area": "25 Acres",
                "total_units": "1113 Units",
                "towers": "7 Towers",
                "completion_date": "Dec 2028",
                "is_prioritized": True,
            },
            {
                "name": "DLF Cyber City Business Center",
                "sector": "DLF Phase 2",
                "location": "Cyber City, Gurugram",
                "tagline": "Premium Office Spaces",
                "status": "ready_to_move",
                "property_type": "commercial",
                "project_area": "8.5 Acres",
                "total_units": "4 Towers",
                "towers": "4",
                "completion_date": "Delivered",
                "is_prioritized": False,
            }
        ]

        for p_data in projects_data:
            p, p_created = Project.objects.get_or_create(
                name=p_data["name"],
                defaults={"slug": slugify(p_data["name"])}
            )
            p.developer_obj = dlf
            p.developer = dlf.name
            p.sector = p_data["sector"]
            p.location = p_data["location"]
            p.tagline = p_data["tagline"]
            p.status = p_data["status"]
            p.property_type = p_data["property_type"]
            p.project_area = p_data["project_area"]
            p.total_units = p_data["total_units"]
            p.towers = p_data["towers"]
            p.completion_date = p_data["completion_date"]
            p.is_prioritized = p_data["is_prioritized"]
            p.save()

        self.stdout.write(self.style.SUCCESS('Successfully seeded rich data for DLF Limited and its projects.'))
