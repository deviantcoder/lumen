import os
import shutil
import logging

from django.utils import timezone
from django.conf import settings

from celery import shared_task

from .models import Story, Collection

from utils.files import process_obj_media_file


logger = logging.getLogger(__name__)


@shared_task
def delete_expired_stories():

    """
    Celery task that deletes stories that have expired.
    """

    now = timezone.now()

    expired_stories = Story.objects.filter(expires_at__lte=now)
    count = expired_stories.count()

    if count > 0:
        expired_stories.delete()
        logger.info(f'Deleted {count} stories at: {now}.')
    else:
        logger.info(f'No expired stories found at: {now}.')


@shared_task(bind=True, max_retries=3)
def process_story_image_task(self, story_id=None, quality=60):

    """
    Celery task that processes and compresses the
    story image for the given story_id.
    """

    try:
        instance = Story.objects.get(pk=story_id)
        if not instance.media:
            return

        process_obj_media_file(
            obj=instance, file_field='media', quality=quality,
            crop=False, skip_signals=True
        )
    except Story.DoesNotExist:
        logger.error(
            f'Story {story_id} not found for image compression.'
        )
    except Exception as exc:
        logger.warning(
            f'Image compression failed for story: {story_id}: {exc}'
        )
        raise self.retry(countdown=60, exc=exc)


@shared_task(bind=True, max_retries=3)
def delete_story_media_task(self, public_id):

    """
    Celery task that deletes all media files associated
    with the story identified by publid_id.
    """

    try:
        path = os.path.join(
            getattr(settings, 'MEDIA_ROOT'), 'stories', str(public_id)
        )

        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as exc:
        logger.error(
            f'Failed to delete media for story: {public_id}, {exc}'
        )
        raise self.retry(countdown=60, exc=exc)


@shared_task(bind=True, max_retries=3)
def process_collection_image_task(self, collection_id=None, quality=60):

    """
    Celery task that processes and compresses the
    collection image for the given collection_id.
    """

    try:
        instance = Collection.objects.get(pk=collection_id)
        if not instance.image:
            return

        process_obj_media_file(
            obj=instance, file_field='image', quality=quality,
            crop=True, crop_size=400, skip_signals=True
        )
    except Story.DoesNotExist:
        logger.error(
            f'Collection: {collection_id} not found for image compression.'
        )
    except Exception as exc:
        logger.warning(
            f'Image compression failed for collection: {collection_id}: {exc}'
        )
        raise self.retry(countdown=60, exc=exc)


@shared_task(bind=True, max_retries=3)
def delete_collection_media_task(self, public_id):

    """
    Celery task that deletes all media files associated
    with the collection identified by publid_id.
    """

    try:
        path = os.path.join(
            getattr(settings, 'MEDIA_ROOT'), 'collections', str(public_id)
        )

        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as exc:
        logger.error(
            f'Failed to delete media for collection: {public_id}: {exc}'
        )
        raise self.retry(countdown=60, exc=exc)
