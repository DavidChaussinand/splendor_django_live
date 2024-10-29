# jeu/urls.py

from django.urls import path
from . import views
from .views import user_login, user_logout, register
from .views import game_view ,login_view , CreerPartieView , RejoindrePartieView
from .views import GameView




urlpatterns = [
    path('', views.home, name='home'),
    path("login/", login_view, name="login"),
    path('logout/', user_logout, name='logout'),
    path('register/', register, name='register'),  # Ajoute l'URL pour l'inscription
    path("game/", game_view, name="game"),  # Assure-toi que name="game"
    path("prendre_2_jetons/", views.prendre_2_jetons_de_meme_couleur, name="prendre_2_jetons"),
    path('creer_partie/', CreerPartieView.as_view(), name='creer_partie'),
    path('game/<str:nom_partie>/', GameView.as_view(), name='game_view'),
    path('rejoindre_partie/<int:partie_id>/', RejoindrePartieView.as_view(), name='rejoindre_partie'),
    path('reset_game/<int:partie_id>/', views.reset_game, name='reset_game'),
    # Autres URLs...
]
