import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Partie, JoueurPartie, Jeton , Carte
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
        
        elif action == "acheter_carte":
            carte_id = data.get("carte_id")
            await self.handle_acheter_carte(carte_id)


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


    async def handle_acheter_carte(self, carte_id):
        
        carte = await database_sync_to_async(Carte.objects.get)(id=carte_id)
        joueur_partie = await database_sync_to_async(JoueurPartie.objects.get)(joueur=self.user, partie=self.partie)
        await database_sync_to_async(joueur_partie.acheter_carte)(carte)
       
        await self.remove_carte_from_plateau(carte)
    # Récupérer les données mises à jour du joueur
        jetons = await database_sync_to_async(lambda: joueur_partie.jetons)()
        bonus = await database_sync_to_async(lambda: joueur_partie.bonus)()
        points_victoire = await database_sync_to_async(lambda: joueur_partie.points_victoire)()
        # Récupérer les cartes achetées du joueur
        cartes_achetees = await self.get_cartes_achetees(joueur_partie)

        cartes_data = await self.get_cartes_data()

        # Envoyer la mise à jour à tous les clients
        await self.channel_layer.group_send(
            self.partie_group_name,
            {
                "type": "game_update",
                "action": "acheter_carte",
                "message": f"{self.user.username} a acheté la carte {carte_id}.",
                "joueur": self.user.username,
                "jetons": jetons,
                "bonus": bonus,
                "points_victoire": points_victoire,
                "cartes_achetees": cartes_achetees,
                "cartes": cartes_data
            }
        )

        # Passer au joueur suivant
        await self.passer_au_joueur_suivant()

    async def remove_carte_from_plateau(self, carte):
        def sync_remove_carte(partie_id, carte_id):
            partie = Partie.objects.get(id=partie_id)
            plateau = partie.plateau
            plateau.cartes.remove(carte_id)
            plateau.save()

        await database_sync_to_async(sync_remove_carte)(self.partie.id, carte.id)

    async def get_cartes_data(self):
        def sync_get_cartes_data(partie_id):
            partie = Partie.objects.get(id=partie_id)
            plateau = partie.plateau
            cartes = plateau.cartes.all()
            cartes_data = []
            for c in cartes:
                cartes_data.append({
                    'id': c.id,
                    'niveau': c.niveau,
                    'bonus': c.bonus,
                    'points_victoire': c.points_victoire,
                    'cout': c.cout,
                    'image_path': c.image_path,
                })
            return cartes_data

        return await database_sync_to_async(sync_get_cartes_data)(self.partie.id)


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




    async def get_cartes_achetees(self, joueur_partie):
        def sync_get_cartes_achetees(joueur_partie_id):
            joueur_partie = JoueurPartie.objects.get(id=joueur_partie_id)
            cartes = joueur_partie.cartes_achetees.all()
            return [{
                'id': c.id,
                'niveau': c.niveau,
                'bonus': c.bonus,
                'points_victoire': c.points_victoire,
                'image_path': c.image_path,
            } for c in cartes]
        return await database_sync_to_async(sync_get_cartes_achetees)(joueur_partie.id)
