import os

from django.conf import settings
from django.core.management import call_command
from django.db import connections


TRUTHY_VALUES = {'1', 'true', 'yes', 'on'}


def env_flag(name):
    return os.environ.get(name, '').lower() in TRUTHY_VALUES


def default_database_is_postgresql():
    default_database = settings.DATABASES.get('default', {})
    return default_database.get('ENGINE') == 'django.db.backends.postgresql'


def running_on_vercel():
    return os.environ.get('VERCEL') == '1'


def should_run_startup_migrations():
    if not env_flag('AUTO_MIGRATE_ON_STARTUP') and not running_on_vercel():
        return False

    return default_database_is_postgresql()


def run_startup_migrations():
    if not should_run_startup_migrations():
        return

    connection = connections['default']
    with connection.cursor():
        pass

    call_command('migrate', interactive=False, verbosity=0)


def should_sync_sqlite_to_postgres():
    if not default_database_is_postgresql():
        return False

    source_database = settings.DATABASES.get('sqlite_source', {})
    source_path = source_database.get('NAME')
    if not source_path or not os.path.exists(source_path):
        return False

    return env_flag('AUTO_SYNC_SQLITE_TO_POSTGRES') or running_on_vercel()


def sync_sqlite_to_postgres():
    if should_sync_sqlite_to_postgres():
        call_command('sync_sqlite_to_postgres', verbosity=0)


def run_startup_tasks():
    run_startup_migrations()
    sync_sqlite_to_postgres()
