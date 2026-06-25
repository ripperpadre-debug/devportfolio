import os
from django.core.files.storage import FileSystemStorage

try:
    from cloudinary_storage.storage import MediaCloudinaryStorage

    _has_cloudinary = bool(
        os.environ.get('CLOUDINARY_URL')
        or (
            os.environ.get('CLOUDINARY_CLOUD_NAME')
            and os.environ.get('CLOUDINARY_API_KEY')
            and os.environ.get('CLOUDINARY_API_SECRET')
        )
    )
    resume_storage = MediaCloudinaryStorage() if _has_cloudinary else FileSystemStorage()
except ImportError:
    resume_storage = FileSystemStorage()