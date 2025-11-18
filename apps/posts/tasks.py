import os
import shutil
import logging

from django.conf import settings

from celery import shared_task

from .models import PostMedia

from utils.files import (
    ALLOWED_IMAGE_EXTENSIONS,
    compress_image
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
        
        ext = os.path.splitext(instance.file.name)[-1].lower().lstrip('.')
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            return
        
        processed_image = compress_image(
            file=instance.file, quality=quality
        )

        old_image_name = instance.file.name
        if instance.file.storage.exists(old_image_name):
            instance.file.storage.delete(old_image_name)

        instance._skip_signals = True

        instance.file.save(
            instance.file.name, processed_image, save=False
        )
        instance.save(update_fields=['file'])
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
