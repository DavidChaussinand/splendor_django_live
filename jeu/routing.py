# jeu/routing.py

from django.urls import path
from .consumers import GameConsumer

websocket_urlpatterns = [
    path('ws/game/<str:nom_partie>/', GameConsumer.as_asgi()),  # WebSocket pour chaque partie
]
