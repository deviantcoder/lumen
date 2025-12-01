import os
import shutil
import logging

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete, post_save
from django.db import transaction
from django.conf import settings

from .models import Story, Collection
from .tasks import (
    process_story_image_task,
    delete_story_media_task,
    process_collection_image_task,
    delete_collection_media_task
)

from utils.files import (
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS,
    compress_image,
    get_file_ext
)


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Story)
def process_story_media_file(sender, instance, **kwargs):

    """
    Signal to process and compress media file after a Story
    instance is saved, queueing a Celery task depending on file type.
    """

    if getattr(instance, '_skip_signals', False):
        return

    try:
        if instance.media:
            ext = get_file_ext(file_name=instance.media.name)

            if ext in ALLOWED_IMAGE_EXTENSIONS:
                instance.media_type = Story.MEDIA_TYPES.IMAGE
                instance._skip_signals = True

                instance.save(update_fields=['media_type'])

                transaction.on_commit(
                    lambda: process_story_image_task.delay(
                        story_id=instance.pk
                    )
                )
            elif ext in ALLOWED_VIDEO_EXTENSIONS:
                instance.media_type = Story.MEDIA_TYPES.VIDEO
                instance._skip_signals = True
                instance.save(update_fields=['media_type'])

    except Exception as e:
        logger.warning(
            f'Image compression failed for story: {instance.pk}: {e}'
        )


@receiver(post_delete, sender=Story)
def delete_story_media(sender, instance, *args, **kwargs):
    try:
        delete_story_media_task.delay(instance.public_id)
    except Exception as e:
        logger.warning(f'Story media deletion failed: {e}')


@receiver(post_save, sender=Collection)
def process_collection_media_file(sender, instance, **kwargs):
    if getattr(instance, '_skip_signals', False):
        return
    
    if not instance.image:
        return

    try:
        process_collection_image_task.delay(instance.pk)
    except Exception as e:
        logger.warning(f'Story media deletion failed: {e}')

    
@receiver(post_delete, sender=Collection)
def delete_collection_media(sender, instance, *args, **kwargs):
    try:
        delete_collection_media_task.delay(instance.public_id)
    except Exception as e:
        logger.warning(
            f'Collection media deletion failed for: {instance.pk}: {e}'
        )
