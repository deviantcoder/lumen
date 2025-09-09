def activate_social_account(strategy, details, backend, user=None, *args, **kwargs):
    if user and hasattr(user, 'account_activated'):
        if backend.name in ('google-oauth2', 'github'):
            user.account_activated = True
            user.save(update_fields=['account_activated'])

    return {'user': user, **kwargs}