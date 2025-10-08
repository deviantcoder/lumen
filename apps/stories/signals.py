import os
import shutil
import logging

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete

from .models import Story

from utils.files import (
    ALLOWED_IMAGE_EXTENSIONS, compress_image
)


logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Story)
def compress_media_file(sender, instance, **kwargs):
    try:
        if instance.media:
            ext = os.path.splitext(instance.media.name)[-1].lower().lstrip('.')

            if ext in ALLOWED_IMAGE_EXTENSIONS:
                instance.media = compress_image(instance.media)
    except Exception as e:
        logger.warning(f'Image compression failed: {e}')


@receiver(post_delete, sender=Story)
def delete_story_media(sender, instance, *args, **kwargs):
    try:
        path = f'media/stories/{str(instance.public_id)}'

        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        logger.warning(f'Story media deletion failed: {e}')
