import os
import logging
import shortuuid

from PIL import Image
from io import BytesIO

from django.core.files import File
from django.conf import settings
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)


ALLOWED_IMAGE_EXTENSIONS = (
    'jpg', 'jpeg', 'png', 'gif', 'webp'
)

ALLOWED_VIDEO_EXTENSIONS = (
    'mp4', 'mov', 'avi', 'mkv', 'webm'
)


def base_upload_to(instance, filename, base_dir='uploads', id_attr='public_id'):
    ext = os.path.splitext(filename)[-1]
    new_filename = shortuuid.uuid()

    attrs = id_attr.split('.')
    obj = instance

    for attr in attrs:
        obj = getattr(obj, attr, None)
        if obj is None:
            break

    obj_id = obj or getattr(instance, 'pk', 'unknown')

    return f'{base_dir}/{obj_id}/{new_filename}{ext}'


def compress_image(file):
    try:
        with Image.open(file) as image:
            if image.mode in ('P', 'RGBA'):
                image = image.convert('RGB')
            
            image_io = BytesIO()
            name = os.path.splitext('file')[0] + '.jpg'
            image.save(image_io, format='JPEG', quality=60, optimize=True)

            return File(image_io, name=name)

    except Exception as e:
        logger.warning(f'Image compression failed: {e}')
        return file


def validate_file_size(file):
    max_size_mb = getattr(settings, 'MAX_MEDIA_SIZE', 50)
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file.size > max_size_bytes:
        raise ValidationError(f'File size cannot exceed {max_size_mb}')
