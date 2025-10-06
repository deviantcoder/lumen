import os
import shutil
import logging

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete

from .models import PostMedia, Post

from utils.files import (
    ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS, compress_image
)


logger = logging.getLogger(__name__)


@receiver(pre_save, sender=PostMedia)
def compress_media_file(sender, instance, **kwargs):
    try:
        if instance.file:
            ext = os.path.splitext(instance.file.name)[-1].lower().lstrip('.')

            if ext in ALLOWED_IMAGE_EXTENSIONS:
                instance.media_type = PostMedia.MEDIA_TYPES.IMAGE
            else:
                instance.media_type = PostMedia.MEDIA_TYPES.VIDEO

            if ext in ALLOWED_IMAGE_EXTENSIONS:
                instance.file = compress_image(instance.file)
    except Exception as e:
        logger.warning(f'Image compression failed: {e}')


@receiver(post_delete, sender=Post)
def delete_post_media(sender, instance, *args, **kwargs):
    try:
        path = f'media/posts/{str(instance.public_id)}'

        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        logger.warning(f'Post media deletion failed: {e}')
