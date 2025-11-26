import logging

from django.utils import timezone

from celery import shared_task

from .models import Story


logger = logging.getLogger(__name__)


@shared_task
def delete_expired_stories():
    now = timezone.now()

    expired_stories = Story.objects.filter(expires_at__lte=now)
    count = expired_stories.count()

    if count > 0:
        expired_stories.delete()
        logger.info(f'Deleted {count} stories at: {now}.')
    else:
        logger.info(f'No expired stories found at: {now}.')
