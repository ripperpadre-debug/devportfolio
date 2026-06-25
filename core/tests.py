import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from portfolio import settings as portfolio_settings


class CloudinaryStorageTests(SimpleTestCase):
    def test_use_cloudinary_storage_requires_cloudinary_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(portfolio_settings.use_cloudinary_storage())

    def test_use_cloudinary_storage_enables_when_cloudinary_url_present(self):
        with patch.dict(os.environ, {'CLOUDINARY_URL': 'cloudinary://test:test@test'}, clear=True):
            self.assertTrue(portfolio_settings.use_cloudinary_storage())

    def test_environment_loader_uses_example_env_when_dotenv_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            (base_dir / '.env.example').write_text('CLOUDINARY_URL=cloudinary://test:test@test\n', encoding='utf-8')

            with patch.object(portfolio_settings, 'BASE_DIR', base_dir):
                with patch.dict(os.environ, {}, clear=True):
                    portfolio_settings.load_environment_variables()
                    self.assertEqual(os.environ.get('CLOUDINARY_URL'), 'cloudinary://test:test@test')


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

    def test_media_root_falls_back_to_tempdir_when_target_is_not_writable(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            media_dir = Path(tmpdir) / 'read-only-media'
            media_dir.mkdir(parents=True)
            os.chmod(media_dir, 0o555)
            try:
                resolved_path = portfolio_settings.resolve_media_root(media_dir)
            finally:
                os.chmod(media_dir, 0o755)

            self.assertEqual(resolved_path, Path(tempfile.gettempdir()) / 'devportfolio-media')

    def test_media_root_falls_back_when_directory_cannot_accept_new_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            media_dir = Path(tmpdir) / 'media'
            media_dir.mkdir(parents=True)

            with patch('portfolio.settings.os.access', return_value=True), \
                 patch('portfolio.settings.tempfile.NamedTemporaryFile', side_effect=OSError('read-only filesystem')):
                resolved_path = portfolio_settings.resolve_media_root(media_dir)

            self.assertEqual(resolved_path, Path(tempfile.gettempdir()) / 'devportfolio-media')
