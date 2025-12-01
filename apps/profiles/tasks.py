import os
import shutil
import logging

from django.conf import settings

from celery import shared_task

from .models import Profile

from utils.files import process_obj_media_file


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_profile_image_task(self, profile_id=None, crop_size=500, quality=60):
    
    """
    Celery task that processes and compresses the 
    profile image for the given profile_id.
    """
    
    try:
        profile = Profile.objects.get(pk=profile_id)
        if not profile.image:
            return

        process_obj_media_file(
            obj=profile, file_field='image', quality=quality,
            crop=True, crop_size=crop_size, skip_signals=True
        )
    except Profile.DoesNotExist:
        logger.error(
            f'Profile: {profile_id} not found for image compression.'
        )
    except Exception as exc:
        logger.warning(
            f'Image compression failed for profile: {profile_id}: {exc}'
        )
        raise self.retry(countdown=60, exc=exc)


@shared_task(bind=True, max_retries=3)
def delete_profile_media_task(self, public_id):

    """
    Celery task that deletes all media files associated 
    with the profile identified by public_id.
    """

    try:
        path = os.path.join(
            getattr(settings, 'MEDIA_ROOT'), 'profiles', str(public_id)
        )

        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as exc:
        logger.error(
            f'Failed to delete media for profile: {public_id}, {exc}'
        )
        raise self.retry(countdown=60, exc=exc)
