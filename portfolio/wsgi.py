"""
WSGI config for portfolio project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings')

from django.core.wsgi import get_wsgi_application
from portfolio.startup import run_startup_migrations

application = get_wsgi_application()
run_startup_migrations()
