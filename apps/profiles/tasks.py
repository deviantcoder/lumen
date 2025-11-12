import os
import logging

from celery import shared_task

from .models import Profile

from utils.files import (
    crop_and_compress_image,
    ALLOWED_IMAGE_EXTENSIONS
)


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_profile_image_task(self, profile_id=None, crop_size=500, quality=60):
    try:
        profile = Profile.objects.get(pk=profile_id)
        if not profile.image:
            return
        
        ext = os.path.splitext(profile.image.name)[-1].lower().lstrip('.')
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            return
        
        processed_image = crop_and_compress_image(
            image=profile.image, crop_size=crop_size, quality=quality
        )

        profile._skip_signals = True

        old_image_name = profile.image.name
        if profile.image.storage.exists(old_image_name):
            profile.image.storage.delete(old_image_name)

        profile.image.save(
            profile.image.name, processed_image, save=False
        )
        profile.save(update_fields=['image'])

    except Profile.DoesNotExist:
        logger.error(
            f'Profile: {profile_id} not found for image compression.'
        )
    except Exception as exc:
        logger.warning(
            f'Image compression failed for profile: {profile_id}: {exc}'
        )
        raise self.retry(countdown=60, exc=exc)
