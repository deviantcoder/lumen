import os
import logging

from django.dispatch import receiver
from django.db.models.signals import (
    post_save,
    pre_save,
    post_delete
)
from django.contrib.auth import get_user_model

from .models import Profile
from .tasks import (
    process_profile_image_task,
    delete_profile_media_task
)

from utils.files import (
    ALLOWED_IMAGE_EXTENSIONS,
    get_file_ext
)


logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):

    """
    Signal to create a Profile instance whenever a new User is created.
    """

    if created:
        Profile.objects.create(
            user=instance
        )


@receiver(post_save, sender=Profile)
def process_profile_image(sender, instance, **kwargs):
    if getattr(instance, '_skip_signals', False):
        return
    
    if not instance.image:
        return
    
    try:
        process_profile_image_task.delay(instance.pk)
    except Exception as e:
        logger.warning(
            f'Image processing failed for profile: {instance.pk}: {e}'
        )


@receiver(post_delete, sender=Profile)
def delete_profile_media(sender, instance, *args, **kwargs):

    """
    Signal to delete all associated profile files when a Profile
    instance is deleted, triggering a Celery task.
    """

    try:
        delete_profile_media_task.delay(instance.user.public_id)
    except Exception as e:
        logger.warning(
            f'Profile media deletion failed for: {instance.pk}: {e}'
        )
