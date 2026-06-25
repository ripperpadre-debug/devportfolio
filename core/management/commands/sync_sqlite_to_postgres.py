from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand
from django.db import connections
from django.apps import apps


SYNC_MODELS = [
    ('auth', 'User'),
    ('auth', 'Group'),
    ('core', 'Profile'),
    ('core', 'Skill'),
    ('core', 'Project'),
    ('core', 'BlogPost'),
    ('core', 'ContactMessage'),
    ('core', 'SocialShareLog'),
    ('sessions', 'Session'),
    ('admin', 'LogEntry'),
]


class Command(BaseCommand):
    help = 'Copy data from SQLite to PostgreSQL preserving full field precision.'

    def handle(self, *args, **options):
        default = settings.DATABASES.get('default', {})
        if default.get('ENGINE') != 'django.db.backends.postgresql':
            self.stdout.write('Default database is not PostgreSQL; skipping SQLite sync.')
            return

        source = settings.DATABASES.get('sqlite_source', {})
        source_path = Path(source.get('NAME', ''))
        if not source_path.exists():
            self.stdout.write(f'SQLite source not found at {source_path}; skipping sync.')
            return

        with connections['sqlite_source'].cursor(), connections['default'].cursor():
            pass

        for app_label, model_name in SYNC_MODELS:
            model = apps.get_model(app_label, model_name)
            if model is None:
                continue

            source_objects = list(
                model.objects.using('sqlite_source').all().iterator()
            )
            if not source_objects:
                continue

            m2m_fields = [
                f for f in model._meta.local_many_to_many
                if f.remote_field.through._meta.auto_created
            ]

            model.objects.using('default').all().delete()

            for obj in source_objects:
                field_data = {
                    f.attname: getattr(obj, f.attname)
                    for f in model._meta.concrete_fields
                }
                new_obj = model(**field_data)
                new_obj.save_base(raw=True, using='default')

                for m2m in m2m_fields:
                    related_ids = list(
                        getattr(obj, m2m.attname).values_list('pk', flat=True)
                    )
                    if related_ids:
                        through_model = getattr(model, m2m.attname).through
                        through_model.objects.using('default').filter(
                            **{m2m.m2m_column_name(): new_obj.pk}
                        ).delete()
                        for related_id in related_ids:
                            through_model.objects.using('default').create(
                                **{
                                    m2m.m2m_column_name(): new_obj.pk,
                                    m2m.m2m_reverse_name(): related_id,
                                }
                            )

            self.stdout.write(f'  Synced {len(source_objects)} {app_label}.{model_name}')

        self.stdout.write(self.style.SUCCESS('SQLite data synced to PostgreSQL.'))
