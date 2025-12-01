import os
import logging

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db import transaction

from .models import PostMedia, Post
from .tasks import (
    process_postmedia_image_task,
    delete_post_media_task
)

from utils.files import (
    get_file_ext,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS
)


logger = logging.getLogger(__name__)


@receiver(post_save, sender=PostMedia)
def compress_post_media_file(sender, instance, **kwargs):

    """
    Signal to process and compress media files after a PostMedia
    instance is saved, queueing a Celery task depending on file type.
    """

    if getattr(instance, '_skip_signals', False):
        return

    try:
        if instance.file:
            ext = get_file_ext(file_name=instance.file.name)

            if ext in ALLOWED_IMAGE_EXTENSIONS:
                instance.media_type = PostMedia.MEDIA_TYPES.IMAGE
                instance._skip_signals = True

                instance.save(update_fields=['media_type'])

                transaction.on_commit(
                    lambda: process_postmedia_image_task.delay(
                        postmedia_id=instance.pk
                    )
                )
            elif ext in ALLOWED_VIDEO_EXTENSIONS:
                instance.media_type = PostMedia.MEDIA_TYPES.VIDEO
                instance._skip_signals = True
                instance.save(update_fields=['media_type'])

    except Exception as e:
        logger.warning(
            f'Image compression failed for post media: {instance.pk}: {e}'
        )


@receiver(post_delete, sender=Post)
def delete_post_media(sender, instance, *args, **kwargs):

    """
    Signal to delete all associated PostMedia files when a Post
    instance is deleted, triggering a Celery task.
    """

    try:
        delete_post_media_task.delay(instance.public_id)
    except Exception as e:
        logger.warning(f'Post media deletion failed: {e}')
