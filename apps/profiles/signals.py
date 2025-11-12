import os
import shutil
import logging

from django.dispatch import receiver
from django.db.models.signals import (
    post_save,
    pre_save,
    post_delete
)
from django.contrib.auth import get_user_model

from .models import Profile
from .tasks import process_profile_image_task

from utils.files import ALLOWED_IMAGE_EXTENSIONS


logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance
        )


@receiver(pre_save, sender=Profile)
def detect_image_processing_need(sender, instance, **kwargs):
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
    if getattr(instance, '_skip_signals', False):
        return

    if getattr(instance, '_needs_processing', False) and instance.image:
        process_profile_image_task.delay(instance.pk)
        del instance._needs_processing


@receiver(post_delete, sender=Profile)
def delete_profile_media(sender, instance, *args, **kwargs):
    try:
        path = f'media/profiles/{str(instance.user.public_id)}'

        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        logger.warning(f'User media deletion failed: {e}')
