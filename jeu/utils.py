# fichier jeu/utils.py


from .models import  CartePileNiveau1, CartePileNiveau2, CartePileNiveau3
from random import sample

# jeu/utils.py

def generer_plateau(nombre_joueurs):
    if nombre_joueurs == 2:
        quantite_jetons = 4
    elif nombre_joueurs == 3:
        quantite_jetons = 5
    elif nombre_joueurs == 4:
        quantite_jetons = 7
    else:
        raise ValueError("Le nombre de joueurs doit être compris entre 2 et 4.")

    # Initialisation des jetons pour le plateau
    plateau = {
        "noir": quantite_jetons,
        "blanc": quantite_jetons,
        "rouge": quantite_jetons,
        "vert": quantite_jetons,
        "jaune": 5  # Jaune reste toujours à 5
    }
    
    return plateau




def piocher_carte_niveau(plateau, niveau):
    # Sélectionner la pile de cartes du niveau demandé
    if niveau == 1:
        pile = CartePileNiveau1.objects.filter(plateau=plateau).order_by('order')
    elif niveau == 2:
        pile = CartePileNiveau2.objects.filter(plateau=plateau).order_by('order')
    elif niveau == 3:
        pile = CartePileNiveau3.objects.filter(plateau=plateau).order_by('order')
    else:
        return None

    # Vérifier si la pile n'est pas vide
    if pile.exists():
        # Prendre la première carte
        prochaine_carte_relation = pile.first()
        prochaine_carte = prochaine_carte_relation.carte
        # Supprimer la carte de la pile
        prochaine_carte_relation.delete()
        # Réajuster l'ordre des cartes restantes
        for index, relation in enumerate(pile[1:]):
            relation.order = index
            relation.save()
        return prochaine_carte
    else:
        return None  # Si la pile est vide



