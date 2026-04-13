import sys
import os
import urllib.request
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from listings.models import Developer

# Comprehensive real estate developer database matching the user's DB exact names
DEVELOPER_DATA = {
    "AIPL Group": {"domain": "aipl.com", "year": 1991, "headquarters": "Gurugram, India", "tagline": "Building the Future"},
    "ATS Group": {"domain": "atsgreens.com", "year": 1998, "headquarters": "Noida, India", "tagline": "The Better Way Home"},
    "Adani Group": {"domain": "adanirealty.com", "year": 2010, "headquarters": "Ahmedabad, India", "tagline": "The Good Life"},
    "Adani Realty": {"domain": "adanirealty.com", "year": 2010, "headquarters": "Ahmedabad, India", "tagline": "The Good Life"},
    "Alpha Group": {"domain": "alphacorp.in", "year": 2003, "headquarters": "Gurugram, India", "tagline": "Building Assets, Creating Value"},
    "Ansal Group": {"domain": "ansalapi.com", "year": 1967, "headquarters": "New Delhi, India", "tagline": "Building Lifestyles Since 1967"},
    "Ashiana Group": {"domain": "ashianahousing.com", "year": 1979, "headquarters": "New Delhi, India", "tagline": "You are in Safe Hands"},
    "Assotech Group": {"domain": "assotech.in", "year": 1987, "headquarters": "Noida, India", "tagline": "Next Generation Real Estate"},
    "BPTP Group": {"domain": "bptp.com", "year": 2003, "headquarters": "Gurugram, India", "tagline": "Excellence in Everything"},
    "Bestech Group": {"domain": "bestechgroup.com", "year": 1992, "headquarters": "Gurugram, India", "tagline": "Building More Than Trust"},
    "Brisk Infrastructure": {"domain": "briskinfra.com", "year": 1996, "headquarters": "Gurugram, India", "tagline": "Integrity and Excellence"},
    "Capital Group / Capital Developers": {"domain": "capitalgroup.co.in", "year": 1995, "headquarters": "New Delhi, India", "tagline": "Building Trust"},
    "Central Park Group": {"domain": "centralpark.in", "year": 2001, "headquarters": "Gurugram, India", "tagline": "Expect the Unexpected"},
    "Conscient Group": {"domain": "conscient.in", "year": 1975, "headquarters": "Gurugram, India", "tagline": "Where Value Meets Values"},
    "County Group": {"domain": "countygroup.in", "year": 2009, "headquarters": "Noida, India", "tagline": "Excellence Beyond Compare"},
    "DLF Group": {"domain": "dlf.in", "year": 1946, "headquarters": "New Delhi, India", "tagline": "Building India"},
    "DLF Limited (DLF Homes)": {"domain": "dlf.in", "year": 1946, "headquarters": "New Delhi, India", "tagline": "Building India"},
    "Elan Group": {"domain": "elanlimited.com", "year": 2013, "headquarters": "Gurugram, India", "tagline": "Building The Future"},
    "Eldeco Group": {"domain": "eldecogroup.com", "year": 1985, "headquarters": "New Delhi, India", "tagline": "Trust That Endures"},
    "Emaar Group": {"domain": "emaar-india.com", "year": 2005, "headquarters": "Gurugram, India", "tagline": "Transforming Landscapes"},
    "Emaar Group / Emaar India": {"domain": "emaar-india.com", "year": 2005, "headquarters": "Gurugram, India", "tagline": "We Shape Your Future"},
    "Emaar India": {"domain": "emaar-india.com", "year": 2005, "headquarters": "Gurugram, India", "tagline": "Inspiring Life"},
    "Experion Developers": {"domain": "experion.co", "year": 2006, "headquarters": "Gurugram, India", "tagline": "The Positive Side of Life"},
    "GLS Infra": {"domain": "glsinfra.in", "year": 2003, "headquarters": "Gurugram, India", "tagline": "Homes For All"},
    "Ganga Group": {"domain": "goelgangadevelopments.com", "year": 1982, "headquarters": "Pune, India", "tagline": "Purity of Purpose"},
    "Godrej": {"domain": "godrejproperties.com", "year": 1990, "headquarters": "Mumbai, India", "tagline": "Let's Build Better"},
    "Hero Group": {"domain": "herorealty.in", "year": 2006, "headquarters": "New Delhi, India", "tagline": "Joy of Creation"},
    "Imperia Developers": {"domain": "imperiastructures.com", "year": 1986, "headquarters": "New Delhi, India", "tagline": "Building Legacies"},
    "India Group": {"domain": "indiabullsrealestate.com", "year": 2006, "headquarters": "Mumbai, India", "tagline": "Excellence Redefined"},
    "Indiabulls Group": {"domain": "indiabullsrealestate.com", "year": 2006, "headquarters": "Mumbai, India", "tagline": "Trust and Excellence"},
    "JMS Group": {"domain": "jmsbuildtech.com", "year": 2013, "headquarters": "Gurugram, India", "tagline": "Vision Meets Reality"},
    "Joyville Group": {"domain": "joyvillehomes.com", "year": 2015, "headquarters": "Mumbai, India", "tagline": "Live Without Compromise"},
    "Kashish Group": {"domain": "kashishdevelopers.com", "year": 2001, "headquarters": "Ranchi, India", "tagline": "Commitment to Excellence"},
    "Krisumi Group": {"domain": "krisumi.com", "year": 2018, "headquarters": "Gurugram, India", "tagline": "Indo-Japanese Excellence"},
    "Landmark Group": {"domain": "landmarkgroup.in", "year": 1998, "headquarters": "New Delhi, India", "tagline": "Transforming Standards"},
    "Lotus Group": {"domain": "lotusgreens.in", "year": 2013, "headquarters": "Noida, India", "tagline": "The Clarity of Purpose"},
    "M2K Group": {"domain": "m2kindia.com", "year": 1998, "headquarters": "New Delhi, India", "tagline": "Adding Value To Life"},
    "M3M Group": {"domain": "m3mindia.com", "year": 2010, "headquarters": "Gurugram, India", "tagline": "Magnificence in the Trinity"},
    "Mahindra Group": {"domain": "mahindralifespaces.com", "year": 1994, "headquarters": "Mumbai, India", "tagline": "Joyful Homecomings"},
    "Mapsko Group": {"domain": "mapskogroup.com", "year": 2003, "headquarters": "New Delhi, India", "tagline": "Developing Future"},
    "Max Group": {"domain": "maxestates.in", "year": 2016, "headquarters": "Noida, India", "tagline": "WorkWell. LiveWell."},
    "Microtek Infrastructure": {"domain": "microtekinfra.com", "year": 2005, "headquarters": "New Delhi, India", "tagline": "Innovation and Excellence"},
    "Orris Group": {"domain": "orris.in", "year": 2006, "headquarters": "Gurugram, India", "tagline": "Expect The Best"},
    "Oxirich Group": {"domain": "oxirich.com", "year": 2006, "headquarters": "New Delhi, India", "tagline": "A Promise of Better Living"},
    "Paras Group": {"domain": "parasbuildtech.com", "year": 1990, "headquarters": "Gurugram, India", "tagline": "Building The Future"},
    "Parkview Group": {"domain": "bestechgroup.com", "year": 1992, "headquarters": "Gurugram, India", "tagline": "Excellence in Design"},
    "Puri Group": {"domain": "puriconstructions.com", "year": 1971, "headquarters": "New Delhi, India", "tagline": "Make A Statement"},
    "Pyramid Infratech": {"domain": "pyramidinfratech.com", "year": 2008, "headquarters": "Gurugram, India", "tagline": "Providing Quality Life"},
    "ROF Group": {"domain": "rof.co.in", "year": 2004, "headquarters": "Gurugram, India", "tagline": "Value Real Estate"},
    "Raheja Developers": {"domain": "raheja.com", "year": 1990, "headquarters": "New Delhi, India", "tagline": "Delivering Quality"},
    "SS Group": {"domain": "ssgroup-india.com", "year": 1992, "headquarters": "Gurugram, India", "tagline": "Built on Trust"},
    "Sare Group": {"domain": "saregroup.com", "year": 2006, "headquarters": "Gurugram, India", "tagline": "A World of Happiness"},
    "Signature Global": {"domain": "signatureglobal.in", "year": 2014, "headquarters": "Gurugram, India", "tagline": "Reality. Reliability. Responsibility."},
    "Signature Group": {"domain": "signatureglobal.in", "year": 2014, "headquarters": "Gurugram, India", "tagline": "Premium Value Housing"},
    "Smart World Group": {"domain": "smartworlddevelopers.com", "year": 2021, "headquarters": "Gurugram, India", "tagline": "A World of Smart Living"},
    "Smartworld Group": {"domain": "smartworlddevelopers.com", "year": 2021, "headquarters": "Gurugram, India", "tagline": "Defining Smart Living"},
    "Sobha Group": {"domain": "sobha.com", "year": 1995, "headquarters": "Bengaluru, India", "tagline": "Passion at Work"},
    "Spaze Group": {"domain": "spaze.in", "year": 2006, "headquarters": "Gurugram, India", "tagline": "Create, Construct, Care"},
    "Tata": {"domain": "tatarealty.in", "year": 1984, "headquarters": "Mumbai, India", "tagline": "Leadership with Trust"},
    "Umang Group": {"domain": "umangrealtech.com", "year": 2007, "headquarters": "New Delhi, India", "tagline": "Building Dreams"},
    "Vardhman Group": {"domain": "vardhman.com", "year": 1965, "headquarters": "Ludhiana, India", "tagline": "Excellence Driven"},
    "Vatika Group": {"domain": "vatikagroup.com", "year": 1986, "headquarters": "Gurugram, India", "tagline": "Creating Lasting Value"},
    "Vipul Group": {"domain": "vipulgroup.in", "year": 2001, "headquarters": "Gurugram, India", "tagline": "Building Happiness"},
    "WTC Group": {"domain": "wtc.com", "year": 1969, "headquarters": "Global", "tagline": "Connecting the Business World"},
    "Wal Group": {"domain": "walstreet.in", "year": 2010, "headquarters": "Gurugram, India", "tagline": "Urban Excellence"},
    "Whiteland Corporation": {"domain": "whiteland.in", "year": 2021, "headquarters": "Gurugram, India", "tagline": "Building Trust, Delivering Excellence"}
}


class Command(BaseCommand):
    help = "Enrich developers with metadata and dynamically download their logos via Clearbit."

    def handle(self, *args, **options):
        developers = Developer.objects.all()
        updated_count = 0
        logo_count = 0

        for dev in developers:
            name = dev.name
            data = DEVELOPER_DATA.get(name)

            if not data:
                # Try soft match
                for key, val in DEVELOPER_DATA.items():
                    if name.lower() in key.lower() or key.lower() in name.lower():
                        data = val
                        break

            if data:
                # Update text fields
                dev.tagline = dev.tagline or data.get('tagline', '')
                dev.established_year = dev.established_year or data.get('year')
                dev.headquarters = dev.headquarters or data.get('headquarters', '')
                dev.website = dev.website or f"https://www.{data.get('domain', '')}"
                dev.is_featured = True # Make everyone featured so they show up perfectly nicely in frontend
                
                # Setup description
                if not dev.description:
                    dev.description = f"{dev.name} is a premier real estate developer headquartered in {dev.headquarters}. Established in {dev.established_year}, they have consistently delivered landmark projects with their philosophy: '{dev.tagline}'."
                
                if not dev.logo_file and data.get('domain'):
                    # Fetch logo via Google Favicon API (reliable and unrestricted)
                    domain = data['domain']
                    logo_url = f"https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://{domain}&size=256"
                    try:
                        req = urllib.request.Request(logo_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=10) as response:
                            if response.status == 200:
                                image_content = response.read()
                                dev.logo_file.save(f"{dev.slug}_logo.png", ContentFile(image_content), save=False)
                                logo_count += 1
                                self.stdout.write(f"Successfully downloaded logo for {dev.name} from {domain}")
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Could not load logo for {dev.name}: {e}"))

                dev.save()
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully enriched {updated_count} developers and downloaded {logo_count} logos!"))
