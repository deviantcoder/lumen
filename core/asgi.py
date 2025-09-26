import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django_asgi_application = get_asgi_application()


application = ProtocolTypeRouter({
    'http': django_asgi_application,
    # 'websocket': ''
})
