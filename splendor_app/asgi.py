import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "splendor_app.settings")

import django
django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from jeu.routing import websocket_urlpatterns

from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter({
    "http": ASGIStaticFilesHandler(django_asgi_app),  # Gère les fichiers statiques avec ASGIStaticFilesHandler
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})