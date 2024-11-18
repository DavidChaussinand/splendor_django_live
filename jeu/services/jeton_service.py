from channels.db import database_sync_to_async
from .joueur_service import JoueurService

class JetonService:
    @staticmethod
    @database_sync_to_async
    def get_jeton_disponible(partie, couleur):
        plateau = partie.plateau
        jeton = plateau.jetons.get(couleur=couleur)
        return jeton.quantite

    @staticmethod
    @database_sync_to_async
    def update_jeton_disponible(partie, couleur, quantite):
        plateau = partie.plateau
        jeton = plateau.jetons.get(couleur=couleur)
        jeton.quantite += quantite
        jeton.save()

    @staticmethod
    @database_sync_to_async
    def get_couleurs_disponibles(partie):
        """
        Récupère les couleurs disponibles (sans les jaunes) et leurs quantités pour une partie donnée.
        """
        plateau = partie.plateau
        # Exclure les jaunes
        couleurs_disponibles = plateau.couleurs_disponibles()
        return {couleur: quantite for couleur, quantite in couleurs_disponibles.items() if couleur != "jaune"}

    @staticmethod
    @database_sync_to_async
    def get_nombre_couleurs_disponibles(partie):
        """
        Récupère le nombre de couleurs disponibles (sans les jaunes) pour une partie donnée.
        """
        plateau = partie.plateau
        # Exclure les jaunes
        couleurs_disponibles = plateau.couleurs_disponibles()
        couleurs_sans_jaune = {couleur: quantite for couleur, quantite in couleurs_disponibles.items() if couleur != "jaune"}
        return len(couleurs_sans_jaune)


    @staticmethod
    async def prendre_2_jetons(partie, joueur, couleur):
        # Vérifier si la couleur est jaune
        if couleur == "jaune":
            return {"error": "Impossible de prendre un jeton jaune avec cette action."}

        jeton_disponible = await JetonService.get_jeton_disponible(partie, couleur)

        if jeton_disponible < 4:
            return {"error": f"Il faut au moins 4 jetons {couleur} sur le plateau pour prendre 2."}
        if jeton_disponible < 2:
            return {"error": f"Pas assez de jetons {couleur} pour en prendre 2."}

        # Mettre à jour les jetons du plateau
        await JetonService.update_jeton_disponible(partie, couleur, -2)

        # Mettre à jour les jetons du joueur
        joueur_partie = await JoueurService.get_joueur_partie(joueur, partie)
        await JoueurService.update_joueur_jetons(joueur_partie, couleur, 2)

        quantite_restant = jeton_disponible - 2

        # Préparer le message de succès
        message = {
            "type": "game_update",
            "message": f"{joueur.username} a pris 2 jetons {couleur}.",
            "couleur": couleur,
            "quantite_restant": quantite_restant,
            "joueur": joueur.username,
        }

        return {"success": message}
    
    @staticmethod
    async def prendre_3_jetons_differents(partie, joueur, couleurs):
        couleurs_disponibles = await JetonService.get_couleurs_disponibles(partie)
        nombre_couleurs_disponibles = len(couleurs_disponibles)
            
        prises = []
        joueur_partie = await JoueurService.get_joueur_partie(joueur, partie)

        
        # Scénario 1 : 3 couleurs ou plus disponibles
        if nombre_couleurs_disponibles >= 3:
            if len(couleurs) != 3:
                return {"error": "Vous devez sélectionner exactement 3 couleurs différentes."}
            if not set(couleurs).issubset(set(couleurs_disponibles.keys())):
                return {"error": "Une ou plusieurs couleurs sélectionnées ne sont pas disponibles sur le plateau."}

        # Scénario 2 : 2 couleurs disponibles
        elif nombre_couleurs_disponibles == 2:
            if set(couleurs) != set(couleurs_disponibles.keys()):
                return {"error": f"Vous devez sélectionner exactement ces 2 couleurs : {', '.join(couleurs_disponibles.keys())}."}

        # Scénario 3 : 1 couleur disponible
        elif nombre_couleurs_disponibles == 1:
            seule_couleur = list(couleurs_disponibles.keys())[0]
            if couleurs != [seule_couleur]:
                return {"error": f"Vous devez sélectionner cette couleur : {seule_couleur}."}

        # Si aucune couleur n'est disponible (sans compter les jaunes)
        elif nombre_couleurs_disponibles == 0:
            return {"error": "Aucune couleur disponible pour prendre des jetons."}


        for couleur in couleurs:
            # Vérifier si la couleur est jaune
            if couleur == "jaune":
                return {"error": "Impossible de prendre un jeton jaune avec cette action."}

            # Vérifier la disponibilité du jeton
            jeton_disponible = await JetonService.get_jeton_disponible(partie, couleur)
            if jeton_disponible >= 1:
                # Mettre à jour les jetons du plateau et du joueur
                await JetonService.update_jeton_disponible(partie, couleur, -1)
                await JoueurService.update_joueur_jetons(joueur_partie, couleur, 1)
                prises.append(couleur)
            else:
                return {"error": f"Pas assez de jetons {couleur} pour en prendre un."}

        

        message = {
            "type": "game_update",
            "message": f"{joueur.username} a pris un jeton de chaque couleur : {', '.join(prises)}.",
            "couleurs": prises,
            "joueur": joueur.username,
            
        }

        return {"success": message}
