import os
import shutil
import logging

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth import get_user_model

from .models import Profile

from utils.files import compress_image


logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance
        )


@receiver(pre_save, sender=Profile)
def compress_profile_image(sender, instance, **kwargs):
    if not instance.image:
        return
    
    try:
        if instance.pk:
            old_image = Profile.objects.filter(pk=instance.pk).values_list('image', flat=True).first()
            if old_image and old_image == instance.image:
                return
    except Exception as e:
        logger.warning(f'Image compression failed: {e}')

    try:
        instance.image = compress_image(instance.image)
    except Exception as e:
        logger.warning(f'Image compression failed: {e}')


@receiver(post_delete, sender=Profile)
def delete_profile_media(sender, instance, *args, **kwargs):
    try:
        path = f'media/profiles/{str(instance.user.public_id)}'

        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        logger.warning(f'User media deletion failed: {e}')
