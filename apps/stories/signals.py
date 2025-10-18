import os
import shutil
import logging

from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete

from .models import Story, Collection

from utils.files import (
    ALLOWED_IMAGE_EXTENSIONS, compress_image
)


logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Story)
def compress_story_media_file(sender, instance, **kwargs):
    try:
        if instance.media:
            ext = os.path.splitext(instance.media.name)[-1].lower().lstrip('.')

            if ext in ALLOWED_IMAGE_EXTENSIONS:
                instance.media = compress_image(instance.media)
                instance.story_type = Story.STORY_TYPES.IMAGE
            else:
                instance.story_type = Story.STORY_TYPES.VIDEO
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


@receiver(pre_save, sender=Collection)
def compress_collection_media_file(sender, instance, **kwargs):
    try:
        if not instance.pk:
            if instance.image:
                ext = os.path.splitext(instance.image.name)[-1].lower().lstrip('.')
                
                if ext in ALLOWED_IMAGE_EXTENSIONS:
                    instance.image = compress_image(instance.image)
        else:
            old_instance = Collection.objects.filter(pk=instance.pk).first()

            if not old_instance:
                return
            
            if instance.image and instance.image != old_instance.image:
                ext = os.path.splitext(instance.image.name)[-1].lower().lstrip('.')

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
