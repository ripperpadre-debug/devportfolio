from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand
from django.db import connections
from django.apps import apps


# Ordered by FK dependency (parents before children).
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
    help = (
        'Insert missing rows from SQLite into PostgreSQL without overwriting '
        'existing production data.'
    )

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

        total_inserted = 0

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

            target_pks = set(
                model.objects.using('default')
                .values_list('pk', flat=True)
            )

            inserted = 0
            for obj in source_objects:
                if obj.pk in target_pks:
                    continue

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
                        for related_id in related_ids:
                            through_model.objects.using('default').get_or_create(
                                **{
                                    m2m.m2m_column_name(): new_obj.pk,
                                    m2m.m2m_reverse_name(): related_id,
                                }
                            )

                inserted += 1
                total_inserted += 1

            if inserted:
                self.stdout.write(
                    f'  Inserted {inserted} new {app_label}.{model_name} '
                    f'({len(source_objects) - inserted} already existed)'
                )

        if total_inserted == 0:
            self.stdout.write(self.style.SUCCESS('PostgreSQL is already in sync — nothing to insert.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'SQLite data synced to PostgreSQL ({total_inserted} rows inserted).'))
