import logging
import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils.encoding import force_bytes

from celery import shared_task

from .tokens import account_activation_token_generator


logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task(bind=True, max_retries=3)
def send_activation_email_task(self, user_id):
    try:
        user = User.objects.get(pk=user_id)

        if user.last_activation_email_sent:
            now = timezone.now()
            cooldown_delta = now - user.last_activation_email_sent

            if cooldown_delta < datetime.timedelta(
                minutes=getattr(settings, 'EMAIL_RESEND_COOLDOWN', 5)
            ):
                logger.info(
                    f'Activation email for user: {user.username}, skipped due to cooldown.'
                )
                return
            
        public_id = urlsafe_base64_encode(force_bytes(str(user.public_id)))
        token = account_activation_token_generator.make_token(user)

        activation_url = getattr(settings, 'DOMAIN', '127.0.0.1') + reverse(
            'accounts:activate_account',
            kwargs={
                'uidb64': public_id,
                'token': token
            }
        )

        subject = 'Account activation.'

        message = render_to_string(
            'accounts/activation/activation_email.html',
            {
                'user': user,
                'activation_url': activation_url
            }
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'EMAIL_HOST_USER'),
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False
        )

        user.last_activation_email_sent = timezone.now()
        user.save(update_fields=['last_activation_email_sent'])

    except User.DoesNotExist:
        logger.warning(f'User with id: {user_id} does not exist.')
    except Exception as exc:
        logger.warning(f'Failed to send activation email: {exc}')
        raise self.retry(countdown=60, exc=exc, max_retries=3)