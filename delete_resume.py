import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')
django.setup()

from core.models import Profile

p = Profile.objects.first()
if p:
    print(f"Before: resume = {p.resume.name}")
    p.resume.delete()  # Delete the file from Cloudinary
    p.resume = None    # Clear the database field
    p.save()
    print("Resume deleted from database and Cloudinary")
else:
    print("No profile found")
