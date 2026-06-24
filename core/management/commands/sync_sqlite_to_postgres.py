from pathlib import Path
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.core.management import BaseCommand, call_command
from django.db import connections


class Command(BaseCommand):
    help = 'Copy data from the configured SQLite source database into PostgreSQL.'

    def handle(self, *args, **options):
        default_database = settings.DATABASES.get('default', {})
        if default_database.get('ENGINE') != 'django.db.backends.postgresql':
            self.stdout.write('Default database is not PostgreSQL; skipping SQLite sync.')
            return

        source_database = settings.DATABASES.get('sqlite_source', {})
        source_path = Path(source_database.get('NAME', ''))
        if not source_path.exists():
            self.stdout.write(f'SQLite source database not found at {source_path}; skipping sync.')
            return

        with connections['sqlite_source'].cursor():
            pass
        with connections['default'].cursor():
            pass

        with NamedTemporaryFile(suffix='.json') as fixture:
            call_command(
                'dumpdata',
                database='sqlite_source',
                output=fixture.name,
                natural_foreign=True,
                natural_primary=True,
                exclude=['contenttypes', 'auth.Permission'],
                verbosity=0,
            )
            call_command(
                'loaddata',
                fixture.name,
                database='default',
                verbosity=0,
            )

        self.stdout.write(self.style.SUCCESS('SQLite data synced to PostgreSQL.'))
