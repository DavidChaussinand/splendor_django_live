from channels.db import database_sync_to_async
from ..models import Partie

class PartieService:
    @staticmethod
    @database_sync_to_async
    def get_partie(nom_partie):
        return Partie.objects.get(nom=nom_partie)

    @staticmethod
    @database_sync_to_async
    def get_joueur_courant(partie):
        return partie.joueur_courant

    @staticmethod
    @database_sync_to_async
    def passer_au_joueur_suivant(partie):
        prochain_joueur = partie.joueur_suivant()
        partie.joueur_courant = prochain_joueur
        partie.save()
        return prochain_joueur
