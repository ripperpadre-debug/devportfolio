import os

from django.conf import settings
from django.core.management import call_command
from django.db import connections


TRUTHY_VALUES = {'1', 'true', 'yes', 'on'}


def should_run_startup_migrations():
    enabled = os.environ.get('AUTO_MIGRATE_ON_STARTUP', '')
    running_on_vercel = os.environ.get('VERCEL') == '1'
    if enabled.lower() not in TRUTHY_VALUES and not running_on_vercel:
        return False

    default_database = settings.DATABASES.get('default', {})
    return default_database.get('ENGINE') == 'django.db.backends.postgresql'


def run_startup_migrations():
    if not should_run_startup_migrations():
        return

    connection = connections['default']
    with connection.cursor():
        pass

    call_command('migrate', interactive=False, verbosity=0)
