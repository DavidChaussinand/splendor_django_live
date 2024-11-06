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

        joueur_partie = await database_sync_to_async(JoueurPartie.objects.get)(joueur=self.user, partie=self.partie)
        if joueur_partie.tokens_a_defausser > 0:
            jetons_joueur = joueur_partie.jetons
            await self.send(text_data=json.dumps({
                "type": "discard_tokens",
                "message": f"Vous avez {sum(jetons_joueur.values())} jetons, vous devez défausser {joueur_partie.tokens_a_defausser} jeton(s).",
                "jetons": jetons_joueur,
                "tokens_to_discard": joueur_partie.tokens_a_defausser,
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.partie_group_name, self.channel_name)


    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        # Actualiser le joueur courant depuis la base de données
        self.partie = await PartieService.get_partie(self.nom_partie)
        joueur_courant = await PartieService.get_joueur_courant(self.partie)
        joueur_partie = await database_sync_to_async(JoueurPartie.objects.get)(joueur=self.user, partie=self.partie)
        

            # Vérifier si le joueur doit défausser des jetons
        if joueur_partie.tokens_a_defausser > 0 and action != "defausser_jetons":
            await self.send(text_data=json.dumps({"error": "Vous devez d'abord défausser des jetons."}))
            return

        if joueur_courant != self.user:
            await self.send(text_data=json.dumps({"error": "Ce n'est pas votre tour."}))
            return

        if joueur_courant != self.user:
            await self.send(text_data=json.dumps({"error": "Ce n'est pas votre tour."}))
            return

        if action == "prendre_2_jetons":
            couleur = data.get("couleur")
            await self.handle_prendre_2_jetons(couleur)

        elif action == "prendre_3_jetons":
            couleurs = data.get("couleurs")
            await self.handle_prendre_3_jetons(couleurs)
        
        elif action == "defausser_jetons":
            jetons_a_defausser = data.get("jetons_a_defausser")
            await self.handle_defausser_jetons(jetons_a_defausser)
        
        elif action == "acheter_carte":
            carte_id = data.get("carte_id")
            await self.handle_acheter_carte(carte_id)

        elif action == "reserver_carte":
            carte_id = data.get("carte_id")
            await self.handle_reserver_carte(carte_id)

        elif action == "acheter_carte_reservee":
            carte_id = data.get("carte_id")
            await self.handle_acheter_carte_reservee(carte_id)


    async def handle_prendre_2_jetons(self, couleur):
        result = await JetonService.prendre_2_jetons(self.partie, self.user, couleur)

        if "error" in result:
            await self.send(text_data=json.dumps({"error": result["error"]}))
            return

        # Récupérer les données mises à jour
        joueur_partie = await database_sync_to_async(JoueurPartie.objects.get)(joueur=self.user, partie=self.partie)
        jetons_joueur = await database_sync_to_async(lambda: joueur_partie.jetons)()
        plateau_jetons = await database_sync_to_async(lambda: {j.couleur: j.quantite for j in self.partie.plateau.jetons.all()})()


        total_tokens = sum(jetons_joueur.values())

        if total_tokens > 10:
            joueur_partie.tokens_a_defausser = total_tokens - 10
            await database_sync_to_async(joueur_partie.save)()
            # Envoyer une notification au joueur pour défausser des jetons
            await self.send(text_data=json.dumps({
                "type": "discard_tokens",
                "message": f"Vous avez {total_tokens} jetons, vous devez défausser {joueur_partie.tokens_a_defausser} jeton(s).",
                "jetons": jetons_joueur,
                "tokens_to_discard": joueur_partie.tokens_a_defausser,
            }))
            return  # Ne pas passer au joueur suivant pour l'instant
        # Envoyer la mise à jour à tous les clients connectés à la partie
        await self.channel_layer.group_send(
            self.partie_group_name,
            {
                "type": "game_update",
                "action": "prendre_2_jetons",
                "message": f"{self.user.username} a pris 2 jetons {couleur}.",
                "joueur": self.user.username,
                "jetons": jetons_joueur,
                "plateau_jetons": plateau_jetons,
            }
        )

        # Passer au joueur suivant
        await self.passer_au_joueur_suivant()

    async def handle_prendre_3_jetons(self, couleurs):
        result = await JetonService.prendre_3_jetons_differents(self.partie, self.user, couleurs)

        if "error" in result:
            await self.send(text_data=json.dumps({"error": result["error"]}))
            return

        # Récupérer les données mises à jour
        joueur_partie = await database_sync_to_async(JoueurPartie.objects.get)(joueur=self.user, partie=self.partie)
        jetons_joueur = await database_sync_to_async(lambda: joueur_partie.jetons)()
        plateau_jetons = await database_sync_to_async(lambda: {j.couleur: j.quantite for j in self.partie.plateau.jetons.all()})()

        total_tokens = sum(jetons_joueur.values())

        if total_tokens > 10:
            joueur_partie.tokens_a_defausser = total_tokens - 10
            await database_sync_to_async(joueur_partie.save)()
            # Envoyer une notification au joueur pour défausser des jetons
            await self.send(text_data=json.dumps({
                "type": "discard_tokens",
                "message": f"Vous avez {total_tokens} jetons, vous devez défausser {joueur_partie.tokens_a_defausser} jeton(s).",
                "jetons": jetons_joueur,
                "tokens_to_discard": joueur_partie.tokens_a_defausser,
            }))
            return  # Ne pas passer au joueur suivant pour l'instant

            # Envoyer la mise à jour à tous les clients connectés à la partie
        await self.channel_layer.group_send(
            self.partie_group_name,
            {
                "type": "game_update",
                "action": "prendre_3_jetons",
                "message": f"{self.user.username} a pris 3 jetons de couleurs différentes.",
                "joueur": self.user.username,
                "jetons": jetons_joueur,
                "plateau_jetons": plateau_jetons,
            }
        )

        # Passer au joueur suivant
        await self.passer_au_joueur_suivant()

    async def handle_acheter_carte(self, carte_id):
        carte = await database_sync_to_async(Carte.objects.get)(id=carte_id)
        joueur_partie = await database_sync_to_async(JoueurPartie.objects.get)(joueur=self.user, partie=self.partie)
        plateau = await database_sync_to_async(lambda: self.partie.plateau)()

        try:
            await database_sync_to_async(joueur_partie.acheter_carte)(carte, plateau)
        except ValueError as e:
            await self.send(text_data=json.dumps({"error": str(e)}))
            return

        # Retirer la carte du plateau
        await self.remove_carte_from_plateau(carte)

        # Récupérer les données mises à jour
        jetons = await database_sync_to_async(lambda: joueur_partie.jetons)()
        print("Jetons du joueur après l'achat :", jetons)

        bonus = await database_sync_to_async(lambda: joueur_partie.bonus)()
        points_victoire = await database_sync_to_async(lambda: joueur_partie.points_victoire)()
        cartes_achetees = await self.get_cartes_achetees(joueur_partie)
        cartes_data = await self.get_cartes_data()
        plateau_jetons = await database_sync_to_async(lambda: {j.couleur: j.quantite for j in plateau.jetons.all()})()


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
                "cartes": cartes_data,
                "plateau_jetons": plateau_jetons,
            }
        )

        # Passer au joueur suivant
        await self.passer_au_joueur_suivant()

    async def handle_reserver_carte(self, carte_id):
        carte = await database_sync_to_async(Carte.objects.get)(id=carte_id)
        joueur_partie = await database_sync_to_async(JoueurPartie.objects.get)(joueur=self.user, partie=self.partie)
        plateau = await database_sync_to_async(lambda: self.partie.plateau)()

        try:
            # Réserver la carte et mettre à jour les jetons jaunes
            await database_sync_to_async(joueur_partie.reserver_carte)(carte, plateau)
        except ValueError as e:
            await self.send(text_data=json.dumps({"error": str(e)}))
            return

        # Retirer la carte du plateau
        await self.remove_carte_from_plateau(carte)

        # Ajouter la première carte de la pile à la place de la carte réservée
        if await database_sync_to_async(self.partie.plateau.cartes_pile_niveau_1.exists)():
            nouvelle_carte = await database_sync_to_async(self.partie.plateau.cartes_pile_niveau_1.first)()
            await database_sync_to_async(self.partie.plateau.cartes_pile_niveau_1.remove)(nouvelle_carte)
            await database_sync_to_async(self.partie.plateau.cartes.add)(nouvelle_carte)


        # Récupérer les données mises à jour du joueur et du plateau
        jetons = await database_sync_to_async(lambda: joueur_partie.jetons)()
        cartes_reservees = await self.get_cartes_reservees(joueur_partie)
        plateau_jetons = await database_sync_to_async(lambda: {j.couleur: j.quantite for j in plateau.jetons.all()})()
        cartes_data = await self.get_cartes_data()  # Obtenir les cartes mises à jour du plateau

        
        # Vérifier le nombre total de jetons après réservation
        jetons_joueur = await database_sync_to_async(lambda: joueur_partie.jetons)()
        total_tokens = sum(jetons_joueur.values())

        if total_tokens > 10:
            joueur_partie.tokens_a_defausser = total_tokens - 10
            await database_sync_to_async(joueur_partie.save)()
            # Envoyer une notification au joueur pour défausser des jetons
            await self.send(text_data=json.dumps({
                "type": "discard_tokens",
                "message": f"Vous avez {total_tokens} jetons, vous devez défausser {joueur_partie.tokens_a_defausser} jeton(s).",
                "jetons": jetons_joueur,
                "tokens_to_discard": joueur_partie.tokens_a_defausser,
            }))
            return  # Ne pas passer au joueur suivant pour l'instant


        # Envoyer la mise à jour à tous les clients
        await self.channel_layer.group_send(
            self.partie_group_name,
            {
                "type": "game_update",
                "action": "reserver_carte",
                "message": f"{self.user.username} a réservé la carte {carte_id}.",
                "joueur": self.user.username,
                "jetons": jetons_joueur,
                "cartes_reservees": cartes_reservees,
                "plateau_jetons": plateau_jetons,
                "cartes": cartes_data,  # Inclure les cartes mises à jour
            }
        )

        # Passer au joueur suivant
        await self.passer_au_joueur_suivant()


    # Nouvelle méthode dans GameConsumer
    async def handle_acheter_carte_reservee(self, carte_id):
        carte = await database_sync_to_async(Carte.objects.get)(id=carte_id)
        joueur_partie = await database_sync_to_async(JoueurPartie.objects.get)(joueur=self.user, partie=self.partie)
        plateau = await database_sync_to_async(lambda: self.partie.plateau)()
        bonus = await database_sync_to_async(lambda: joueur_partie.bonus)()
        points_victoire = await database_sync_to_async(lambda: joueur_partie.points_victoire)()

        try:
            # Essayer d'acheter la carte réservée
            await database_sync_to_async(joueur_partie.acheter_carte_reservee)(carte, plateau)
        except ValueError as e:
            await self.send(text_data=json.dumps({"error": str(e)}))
            return

        # Mise à jour des données après l'achat
        jetons = await database_sync_to_async(lambda: joueur_partie.jetons)()
        cartes_achetees = await self.get_cartes_achetees(joueur_partie)
        cartes_reservees = await self.get_cartes_reservees(joueur_partie)
        plateau_jetons = await database_sync_to_async(lambda: {j.couleur: j.quantite for j in plateau.jetons.all()})()

        # Envoyer la mise à jour à tous les clients
        await self.channel_layer.group_send(
            self.partie_group_name,
            {
                "type": "game_update",
                "action": "acheter_carte_reservee",
                "message": f"{self.user.username} a acheté une carte réservée.",
                "joueur": self.user.username,
                "jetons": jetons,
                "cartes_achetees": cartes_achetees,
                "cartes_reservees": cartes_reservees,
                "plateau_jetons": plateau_jetons,
                "bonus": bonus,
                "points_victoire": points_victoire,
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
    

    

    async def get_cartes_reservees(self, joueur_partie):
        def sync_get_cartes_reservees(joueur_partie_id):
            joueur_partie = JoueurPartie.objects.get(id=joueur_partie_id)
            cartes = joueur_partie.cartes_reservees.all()
            return [{
                'id': c.id,
                'niveau': c.niveau,
                'bonus': c.bonus,
                'points_victoire': c.points_victoire,
                'image_path': c.image_path,
            } for c in cartes]
        return await database_sync_to_async(sync_get_cartes_reservees)(joueur_partie.id)
    

    async def handle_defausser_jetons(self, jetons_a_defausser):
        joueur_partie = await database_sync_to_async(JoueurPartie.objects.get)(joueur=self.user, partie=self.partie)
        total_tokens_to_discard = joueur_partie.tokens_a_defausser
        total_discarded = sum(jetons_a_defausser.values())

        if total_discarded != total_tokens_to_discard:
            await self.send(text_data=json.dumps({"error": f"Vous devez défausser exactement {total_tokens_to_discard} jeton(s)."}))
            return

        plateau = await database_sync_to_async(lambda: self.partie.plateau)()

        # Défausser les jetons
        for couleur, quantite in jetons_a_defausser.items():
            if quantite > 0:
                if joueur_partie.jetons.get(couleur, 0) >= quantite:
                    joueur_partie.jetons[couleur] -= quantite
                    if joueur_partie.jetons[couleur] == 0:
                        del joueur_partie.jetons[couleur]
                    # Ajouter les jetons défaussés au plateau
                    plateau_jeton = await database_sync_to_async(plateau.jetons.get)(couleur=couleur)
                    plateau_jeton.quantite += quantite
                    await database_sync_to_async(plateau_jeton.save)()
                else:
                    await self.send(text_data=json.dumps({"error": f"Vous n'avez pas assez de jetons {couleur} pour défausser."}))
                    return

        joueur_partie.tokens_a_defausser = 0
        await database_sync_to_async(joueur_partie.save)()

        # Récupérer les données mises à jour
        jetons_joueur = joueur_partie.jetons
        plateau_jetons = await database_sync_to_async(lambda: {j.couleur: j.quantite for j in plateau.jetons.all()})()

        # Envoyer la mise à jour à tous les clients
        await self.channel_layer.group_send(
            self.partie_group_name,
            {
                "type": "game_update",
                "action": "defausser_jetons",
                "message": f"{self.user.username} a défaussé des jetons.",
                "joueur": self.user.username,
                "jetons": jetons_joueur,
                "plateau_jetons": plateau_jetons,
            }
        )

        # Passer au joueur suivant
        await self.passer_au_joueur_suivant()
