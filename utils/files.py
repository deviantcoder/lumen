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


def get_file_ext(file_name: str) -> str:
    ext = os.path.splitext(file_name)[-1].lower().lstrip('.')
    return ext


def base_upload_to(instance, filename, base_dir='uploads', id_attr='public_id'):

    """
    Generate a dynamic file path for uploading files.
    """

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


def compress_image(file, quality: int = 60):

    """
    Compress an image file to JPEG format with specified quality.
    """

    try:
        with Image.open(file) as image:
            if image.mode in ('P', 'RGBA'):
                image = image.convert('RGB')
            
            buffer = BytesIO()
            name = os.path.splitext(file.name)[0] + '.jpg'

            image.save(buffer, format='JPEG', quality=quality, optimize=True)

            buffer.seek(0)

            return File(buffer, name=name)

    except Exception as e:
        logger.warning(f'Image compression failed: {e}')
        return file


def crop_image(file, size: int = 300):

    """
    Crop and resize an image file to a square of specified size."""

    try:
        with Image.open(file) as image:
            if image.mode in ('P', 'RGBA'):
                image = image.convert('RGB')
            
            buffer = BytesIO()
            name = os.path.splitext(file.name)[0] + '.jpg'

            width, height = image.size

            if width != height:
                min_side = min(width, height)
                left = (width - min_side) // 2
                top = (height - min_side) // 2
                right = left + min_side
                bottom = top + min_side
                image = image.crop((left, top, right, bottom))

            image = image.resize((size, size), Image.LANCZOS)
            image.save(buffer, format='JPEG')

            buffer.seek(0)

            return File(buffer, name=name)

    except Exception as e:
        logger.warning(f'Could not resize image: {e}')


def crop_and_compress_image(image, crop_size: int = 300, quality: int = 60):

    """
    Crop and compress an image file.
    """

    cropped = crop_image(image, crop_size)
    compressed = compress_image(cropped, quality)

    return compressed


def validate_file_size(file):

    """
    Validate that the file size does not exceed the maximum allowed size.
    """

    max_size_mb = getattr(settings, 'MAX_MEDIA_SIZE', 50)
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file.size > max_size_bytes:
        raise ValidationError(f'File size cannot exceed {max_size_mb}')


def process_obj_media_file(
        obj, file_field: str='file', quality: int=60, crop: bool=False, 
        crop_size: int=500, skip_signals: bool=False
    ):
    try:
        file = getattr(obj, file_field, None)
        if not file or not file.name:
            return

        ext = get_file_ext(file.name)
        
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            return
        
        if crop:
            processed_image = crop_and_compress_image(
                image=file, crop_size=crop_size, quality=quality
            )
        else:
            processed_image = compress_image(
                file=file, quality=quality
            )

        old_file_name = file.name

        if file.storage.exists(old_file_name):
            file.storage.delete(old_file_name)

        if skip_signals:
            obj._skip_signals = True

        file.save(
            file.name, processed_image, save=False
        )

        obj.save(update_fields=[file_field])
    except Exception as e:
        logger.warning(f'Exception during image processing: {e}')
