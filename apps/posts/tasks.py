import os
import shutil
import logging

from django.conf import settings

from celery import shared_task

from .models import PostMedia

from utils.files import (
    ALLOWED_IMAGE_EXTENSIONS,
    compress_image,
    process_obj_media_file
)


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_postmedia_image_task(self, postmedia_id=None, quality=60):

    """
    Celery task that processes and compresses the 
    post media image for the given postmedia_id.
    """

    try:
        instance = PostMedia.objects.get(pk=postmedia_id)
        if not instance.file:
            return

        process_obj_media_file(
            obj=instance, file_field='file', quality=quality,
            crop=False, skip_signals=True
        )
    except PostMedia.DoesNotExist:
        logger.error(
            f'Post: {postmedia_id} not found.'
        )
    except Exception as exc:
        logger.warning(
            f'Image compression failed for post media: {postmedia_id}: {exc}'
        )
        raise self.retry(countdown=60, exc=exc)
    

@shared_task(bind=True, max_retries=3)
def delete_post_media_task(self, public_id):

    """
    Celery task that deletes all media files associated
    with the post identified by public_id.
    """

    try:
        path = os.path.join(
            getattr(settings, 'MEDIA_ROOT'), 'posts', str(public_id)
        )

        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as exc:
        logger.error(
            f'Failed to delete media for post: {public_id}, {exc}'
        )
        raise self.retry(countdown=60, exc=exc)
