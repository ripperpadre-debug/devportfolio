import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from portfolio import settings as portfolio_settings


class DatabaseConfigTests(SimpleTestCase):
    def test_sqlite_config_uses_custom_path_when_set(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / 'custom.sqlite3'
            with patch.dict(os.environ, {'SQLITE_DB_PATH': str(db_path)}, clear=False):
                config = portfolio_settings.sqlite_database_config()

            self.assertEqual(config['ENGINE'], 'django.db.backends.sqlite3')
            self.assertEqual(config['NAME'], db_path)

    def test_postgres_config_from_neon_url_enables_ssl(self):
        neon_url = 'postgresql://user:password@ep-abc123.us-east-2.aws.neon.tech/neondb?sslmode=require'
        config = portfolio_settings.postgres_database_config_from_url(neon_url)

        self.assertEqual(config['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(config['OPTIONS']['sslmode'], 'require')
