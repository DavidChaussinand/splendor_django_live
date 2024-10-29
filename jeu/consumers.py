import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Partie, JoueurPartie, Jeton
from .services.jeton_service import JetonService
from .services.joueur_service import JoueurService
from .services.partie_service import PartieService

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.nom_partie = self.scope['url_route']['kwargs']['nom_partie']
        self.partie_group_name = f'game_{self.nom_partie}'

        # Vérifier l'authentification
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.partie_group_name, self.channel_name)
        await self.accept()

        # Récupérer la partie et le joueur courant
        self.partie = await PartieService.get_partie(self.nom_partie)
        current_player = await PartieService.get_joueur_courant(self.partie)

        # Envoyer le joueur courant au client lors de la connexion
        await self.send(text_data=json.dumps({
            "type": "tour_update",
            "current_player": current_player.username,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.partie_group_name, self.channel_name)


    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        # Actualiser le joueur courant depuis la base de données
        self.partie = await PartieService.get_partie(self.nom_partie)
        joueur_courant = await PartieService.get_joueur_courant(self.partie)

        if joueur_courant != self.user:
            await self.send(text_data=json.dumps({"error": "Ce n'est pas votre tour."}))
            return

        if action == "prendre_2_jetons":
            couleur = data.get("couleur")
            await self.handle_prendre_2_jetons(couleur)

        elif action == "prendre_3_jetons":
            couleurs = data.get("couleurs")
            await self.handle_prendre_3_jetons(couleurs)


    async def handle_prendre_2_jetons(self, couleur):
        result = await JetonService.prendre_2_jetons(self.partie, self.user, couleur)

        if "error" in result:
            await self.send(text_data=json.dumps({"error": result["error"]}))
            return

        # Envoyer la mise à jour à tous les clients connectés à la partie
        await self.channel_layer.group_send(
            self.partie_group_name,
            result["success"]
        )

        # Passer au joueur suivant
        await self.passer_au_joueur_suivant()

    async def handle_prendre_3_jetons(self, couleurs):
        result = await JetonService.prendre_3_jetons_differents(self.partie, self.user, couleurs)

        if "error" in result:
            await self.send(text_data=json.dumps({"error": result["error"]}))
            return

        # Envoyer la mise à jour à tous les clients connectés à la partie
        await self.channel_layer.group_send(
            self.partie_group_name,
            result["success"]
        )

        # Passer au joueur suivant
        await self.passer_au_joueur_suivant()


    async def passer_au_joueur_suivant(self):
        prochain_joueur = await PartieService.passer_au_joueur_suivant(self.partie)

        # Informer tous les clients du changement de joueur
        await self.channel_layer.group_send(
            self.partie_group_name,
            {
                "type": "tour_update",
                "current_player": prochain_joueur.username,
            }
        )

    async def tour_update(self, event):
        # Envoyer le nom du nouveau joueur courant au client
        await self.send(text_data=json.dumps({
            "type": "tour_update",
            "current_player": event["current_player"],
        }))

    async def game_update(self, event):
        # Envoyer la mise à jour au client
        await self.send(text_data=json.dumps(event))

