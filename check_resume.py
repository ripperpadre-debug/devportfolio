import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')
django.setup()

from core.models import Profile

p = Profile.objects.first()
if p and p.resume:
    print(f"Stored name: {p.resume.name}")
    print(f"Generated URL: {p.resume.url}")
else:
    print("No profile or resume found")
