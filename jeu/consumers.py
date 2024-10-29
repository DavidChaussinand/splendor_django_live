import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Partie, JoueurPartie, Jeton

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

            # Utiliser sync_to_async pour accéder à la base de données
            self.partie = await database_sync_to_async(Partie.objects.get)(nom=self.nom_partie)
            current_player_username = await database_sync_to_async(lambda: self.partie.joueur_courant.username)()

            # Envoyer le joueur courant au client lors de la connexion
            await self.send(text_data=json.dumps({
                "type": "tour_update",
                "current_player": current_player_username,
            }))

        

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.partie_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        # Actualisez le joueur courant depuis la base de données
        self.partie = await database_sync_to_async(Partie.objects.get)(nom=self.nom_partie)
        joueur_courant = await database_sync_to_async(lambda: self.partie.joueur_courant)()

        if joueur_courant != self.user:
            await self.send(text_data=json.dumps({"error": "Ce n'est pas votre tour."}))
            return

        if action == "prendre_2_jetons":
            couleur = data.get("couleur")
            await self.prendre_2_jetons(couleur)

    async def prendre_2_jetons(self, couleur):


        if couleur == "jaune":
            await self.send(text_data=json.dumps({"error": "Impossible de prendre un jeton jaune avec cette action."}))
            return
    
        joueur = await self.get_joueur_partie(self.user, self.nom_partie)
        jeton_disponible = await self.get_jeton_disponible(self.nom_partie, couleur)

        if jeton_disponible >= 4:
            if jeton_disponible >= 2:
                await self.update_jeton_disponible(self.nom_partie, couleur, -2)
                await self.update_joueur_jetons(joueur, couleur, 2)

                quantite_restant = jeton_disponible - 2

                # Envoyer la mise à jour à tous les clients connectés à la partie
                await self.channel_layer.group_send(
                    self.partie_group_name,
                    {
                        "type": "game_update",
                        "message": f"{self.user.username} a pris 2 jetons {couleur}.",
                        "couleur": couleur,
                        "quantite_restant": quantite_restant,
                        "joueur": self.user.username,
                    }
                )
                await self.passer_au_joueur_suivant()
            else:
                await self.send(text_data=json.dumps({"error": f"Pas assez de jetons {couleur} pour en prendre 2."}))
        else:
            await self.send(text_data=json.dumps({"error": f"Il faut au moins 4 jetons {couleur} sur le plateau pour prendre 2."}))

       



    async def passer_au_joueur_suivant(self):
        prochain_joueur = await database_sync_to_async(self.partie.joueur_suivant)()
        self.partie.joueur_courant = prochain_joueur
        await database_sync_to_async(self.partie.save)()
        print("Joueur courant mis à jour en base de données :", self.partie.joueur_courant.username)

        await self.channel_layer.group_send(
            self.partie_group_name,
            {
                "type": "tour_update",
                "current_player": self.partie.joueur_courant.username,
            }
        )

    async def tour_update(self, event):
        # Envoyer le nom du nouveau joueur courant à tous les clients
        await self.send(text_data=json.dumps({
            "type": "tour_update",
            "current_player": event["current_player"],
        }))

    async def game_update(self, event):
        # Envoyer la mise à jour au client
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_joueur_partie(self, user, nom_partie):
        partie = Partie.objects.get(nom=nom_partie)
        return JoueurPartie.objects.get(joueur=user, partie=partie)

    @database_sync_to_async
    def get_jeton_disponible(self, nom_partie, couleur):
        partie = Partie.objects.get(nom=nom_partie)
        plateau = partie.plateau
        jeton = plateau.jetons.get(couleur=couleur)
        return jeton.quantite

    @database_sync_to_async
    def update_jeton_disponible(self, nom_partie, couleur, quantite):
        partie = Partie.objects.get(nom=nom_partie)
        plateau = partie.plateau
        jeton = plateau.jetons.get(couleur=couleur)
        jeton.quantite += quantite
        jeton.save()

    @database_sync_to_async
    def update_joueur_jetons(self, joueur, couleur, quantite):
        joueur.jetons[couleur] = joueur.jetons.get(couleur, 0) + quantite
        joueur.save()
