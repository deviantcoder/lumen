import os
import shutil
import logging

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete
from django.db import transaction

from .models import Story, Collection

from utils.files import (
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS,
    compress_image,
    get_file_ext
)


logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Story)
def compress_story_media_file(sender, instance, **kwargs):

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
        path = f'media/stories/{str(instance.public_id)}'

        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        logger.warning(f'Story media deletion failed: {e}')


@receiver(pre_save, sender=Collection)
def compress_collection_media_file(sender, instance, **kwargs):
    try:
        if not instance.pk:
            if instance.image:
                ext = get_file_ext(instance.image.name)
                
                if ext in ALLOWED_IMAGE_EXTENSIONS:
                    instance.image = compress_image(instance.image)
        else:
            old_instance = Collection.objects.filter(pk=instance.pk).first()

            if not old_instance:
                return
            
            if instance.image and instance.image != old_instance.image:
                ext = os.path.splitext(instance.image.name)[-1].lower().lstrip('.')
                ext = get_file_ext(instance.image.name)

                if ext in ALLOWED_IMAGE_EXTENSIONS:
                    instance.image = compress_image(instance.image)
    except Exception as e:
        logger.warning(f'Story media deletion failed: {e}')

    
@receiver(post_delete, sender=Collection)
def delete_collection_media(sender, instance, *args, **kwargs):
    try:
        path = f'media/collections/{str(instance.public_id)}'

        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        logger.warning(f'Collection media deletion failed: {e}')
