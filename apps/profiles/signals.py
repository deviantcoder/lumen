import os
import shutil
import logging

from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth import get_user_model

from .models import Profile

from utils.files import (
    compress_image, crop_image, ALLOWED_IMAGE_EXTENSIONS, crop_and_compress_image
)


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
    try:
        if not instance.pk:
            if instance.image:
                ext = os.path.splitext(instance.image.name)[-1].lower().lstrip('.')
                
                if ext in ALLOWED_IMAGE_EXTENSIONS:
                    instance.image = crop_and_compress_image(
                        instance.image, crop_size=500, quality=60
                    )
        else:
            old_image = Profile.objects.filter(pk=instance.pk).values_list('image', flat=True).first()

            if not old_image:
                return
            
            if instance.image and instance.image != old_image:
                instance.image = crop_and_compress_image(
                    instance.image, crop_size=500, quality=60
                )
    except Exception as e:
        logger.warning(f'Profile image compression failed: {e}')


@receiver(post_delete, sender=Profile)
def delete_profile_media(sender, instance, *args, **kwargs):
    try:
        path = f'media/profiles/{str(instance.user.public_id)}'

        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        logger.warning(f'User media deletion failed: {e}')
