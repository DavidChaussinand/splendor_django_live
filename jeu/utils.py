# fichier jeu/utils.py

from .models import Jeton

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
