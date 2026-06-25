#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')
django.setup()

from django.test import Client
from core.models import LegalPage

client = Client()

print('TESTING PUBLIC PAGE VISIBILITY:')
print('=' * 50)

# Test Terms page
print('\n1. Testing /terms/ route:')
terms = LegalPage.objects.get(page_type='terms')
response = client.get('/terms/')
print('   Status Code:', response.status_code)
print('   Contains Terms:', 'Terms of Service' in response.content.decode('utf-8'))
print('   Footer contains /terms/:', '/terms/' in response.content.decode('utf-8'))

# Test Privacy page  
print('\n2. Testing /privacy/ route:')
privacy = LegalPage.objects.get(page_type='privacy')
response = client.get('/privacy/')
print('   Status Code:', response.status_code)
print('   Contains Privacy:', 'Privacy Policy' in response.content.decode('utf-8'))
print('   Footer contains /privacy/:', '/privacy/' in response.content.decode('utf-8'))

# Test Home page for footer links
print('\n3. Testing Home page footer:')
response = client.get('/')
print('   Status Code:', response.status_code)
print('   Footer contains /terms/:', '/terms/' in response.content.decode('utf-8'))
print('   Footer contains /privacy/:', '/privacy/' in response.content.decode('utf-8'))
print('   Cookie banner present:', 'cookieBanner' in response.content.decode('utf-8'))
