from channels.db import database_sync_to_async
from ..models import JoueurPartie

class JoueurService:
    @staticmethod
    @database_sync_to_async
    def get_joueur_partie(user, partie):
        return JoueurPartie.objects.get(joueur=user, partie=partie)

    @staticmethod
    @database_sync_to_async
    def update_joueur_jetons(joueur_partie, couleur, quantite):
        joueur_partie.jetons[couleur] = joueur_partie.jetons.get(couleur, 0) + quantite
        joueur_partie.save()
