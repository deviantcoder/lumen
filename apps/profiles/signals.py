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

from utils.files import ALLOWED_IMAGE_EXTENSIONS


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


@receiver(pre_save, sender=Profile)
def detect_image_processing_need(sender, instance, **kwargs):

    """
    Signal to detect if the profile image needs processing before saving.
    """

    if getattr(instance, '_skip_signals', False):
        return

    needs_processing = False

    if not instance.pk:
        if instance.image:
            ext = os.path.splitext(instance.image.name)[-1].lower().lstrip('.')

            if ext in ALLOWED_IMAGE_EXTENSIONS:
                needs_processing = True
    else:
        old_image = (
            sender.objects.filter(
                pk=instance.pk
            )
            .values_list('image', flat=True)
            .first()
        )
        
        if instance.image and instance.image.name != old_image:
            ext = os.path.splitext(instance.image.name)[-1].lower().lstrip('.')

            if ext in ALLOWED_IMAGE_EXTENSIONS:
                needs_processing = True

    if needs_processing:
        instance._needs_processing = True


@receiver(post_save, sender=Profile)
def queue_image_processing(sender, instance, created, **kwargs):

    """
    Signal to process and compress profile image after 
    Profile instance is saved, queueing a Celery task if needed.
    """

    if getattr(instance, '_skip_signals', False):
        return

    if getattr(instance, '_needs_processing', False) and instance.image:
        process_profile_image_task.delay(instance.pk)
        del instance._needs_processing


@receiver(post_delete, sender=Profile)
def queue_profile_media_delete(sender, instance, *args, **kwargs):

    """
    Signal to delete all associated profile files when a Profile
    instance is deleted, triggering a Celery task.
    """

    try:
        delete_profile_media_task.delay(instance.user.public_id)
    except Exception as e:
        logger.warning(f'User media deletion failed: {e}')
