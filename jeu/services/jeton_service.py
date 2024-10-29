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
        prises = []
        joueur_partie = await JoueurService.get_joueur_partie(joueur, partie)
        
        # Vérifier que les couleurs sont distinctes
        if len(set(couleurs)) != 3:
            return {"error": "Vous devez choisir 3 couleurs différentes."}

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
