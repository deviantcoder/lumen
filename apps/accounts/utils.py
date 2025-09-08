import logging
import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import send_mail


logger = logging.getLogger(__name__)

User = get_user_model()


def send_activation_email(user: User):
    try:
        if user:
            if user.last_activation_email_sent:
                now = timezone.now()
                cooldown_delta = now - user.last_activation_email_sent

                if cooldown_delta < datetime.timedelta(minutes=getattr(settings, 'EMAIL_RESEND_COOLDOWN', 5)):
                    logger.info(f'Activation email for @{user.username} skipped due to cooldown.')
                    return False

            token_generator = PasswordResetTokenGenerator()

            public_id = urlsafe_base64_encode(force_bytes(user.public_id))
            token = token_generator.make_token(user)

            activation_url = getattr(settings, 'DOMAIN', '127.0.0.1') + reverse(
                'accounts:activate_account',
                kwargs={
                    'uidb64': public_id,
                    'token': token,
                }
            )

            subject = 'Account Activation'

            message = render_to_string(
                'accounts/activation/activation_email.html',
                {
                    'user': user,
                    'activation_url': activation_url,
                }
            )

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=message
            )

            user.last_activation_email_sent = timezone.now()
            user.save(update_fields=['last_activation_email_sent'])
            
    except Exception as e:
        logger.error(f'Error during sending email verification: {e}')