from django.db import models
from django.contrib.auth.models import User
import json




class Partie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    nombre_joueurs = models.IntegerField()
    joueurs = models.ManyToManyField(User, related_name='parties')
    date_creation = models.DateTimeField(auto_now_add=True)
    joueur_courant = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='parties_en_cours')
    
    def joueur_suivant(self):
        # Récupérer la liste des joueurs ordonnée par ordre d'inscription
        joueurs_partie = JoueurPartie.objects.filter(partie=self).order_by('id')
        joueurs = [jp.joueur for jp in joueurs_partie]
        if self.joueur_courant in joueurs:
            index = joueurs.index(self.joueur_courant)
            index_suivant = (index + 1) % len(joueurs)
            return joueurs[index_suivant]
        else:
            # Si le joueur courant n'est pas dans la liste, on prend le premier
            return joueurs[0]

    def __str__(self):
        return self.nom






class Carte(models.Model):
    niveau = models.PositiveIntegerField()
    cout = models.JSONField(default=dict)
    bonus = models.CharField(max_length=50)  # Couleur de bonus
    points_victoire = models.PositiveIntegerField()


    def __str__(self):
        return f"Carte niveau {self.niveau} avec {self.points_victoire} points et bonus {self.bonus}"
    
    @property
    def image_path(self):
        return f"images/cartes/{self.id}.jpg"
        
    # pour le html <img src="{% static carte.image_path %}" alt="Image de la carte">



class Plateau(models.Model):
    partie = models.OneToOneField(Partie, on_delete=models.CASCADE, related_name='plateau')
    cartes = models.ManyToManyField(Carte, related_name="cartes_visibles")
    cartes_pile_niveau_1 = models.ManyToManyField(Carte, related_name="cartes_pile_niveau_1")
    cartes_pile_niveau_2 = models.ManyToManyField(Carte, related_name="cartes_pile_niveau_2")
    cartes_pile_niveau_3 = models.ManyToManyField(Carte, related_name="cartes_pile_niveau_3")


    def __str__(self):
        return f"Plateau de la partie {self.partie.nom}"



class Jeton(models.Model):
    couleur = models.CharField(max_length=50)
    quantite = models.PositiveIntegerField()
    max_quantite = models.IntegerField(default=7)  # Ajustez la valeur par défaut si nécessaire

    plateau = models.ForeignKey(Plateau, on_delete=models.CASCADE, related_name='jetons', null=True, blank=True)
  

    def __str__(self):
        return f"{self.quantite} jeton(s) {self.couleur} sur {self.plateau}"




    def __str__(self):
        return f"{self.quantite} jeton(s) {self.couleur}"
    
    def ajouter_jetons(self, nombre):
        self.quantite += nombre
        self.save()

    def retirer_jetons(self, nombre):
        if nombre <= self.quantite:
            self.quantite -= nombre
            self.save()
        else:
            raise ValueError("Pas assez de jetons disponibles.")
        

class JoueurPartie(models.Model):
    joueur = models.ForeignKey(User, on_delete=models.CASCADE)
    partie = models.ForeignKey(Partie, on_delete=models.CASCADE, related_name='participants')
    points_victoire = models.IntegerField(default=0)
    jetons = models.JSONField(default=dict)  # Utilisation de JSONField pour stocker les jetons par couleur
    bonus = models.JSONField(default=dict) # Utilisation de JSONField pour stocker les jetons par couleur
    cartes_achetees = models.ManyToManyField('Carte', related_name='achetees', blank=True)  # Liste vide par défaut
    cartes_reservees = models.ManyToManyField('Carte', related_name='reservees', blank=True)  # Liste vide par défaut
    tokens_a_defausser = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"{self.joueur.username} dans {self.partie.nom}"

    def ajouter_jetons(self, couleur, quantite):
        self.jetons[couleur] = self.jetons.get(couleur, 0) + quantite
        self.save()

    def retirer_jetons(self, couleur, quantite):
        if couleur in self.jetons and self.jetons[couleur] >= quantite:
            self.jetons[couleur] -= quantite
            self.save()
        else:
            raise ValueError("Pas assez de jetons disponibles pour cette couleur.")
        
    def acheter_carte(self, carte, plateau):
            # Calculer le coût après application des bonus
            cout_apres_bonus = {}
            for couleur, quantite in carte.cout.items():
                bonus_couleur = self.bonus.get(couleur, 0)
                cout_reduit = max(0, quantite - bonus_couleur)
                cout_apres_bonus[couleur] = cout_reduit

            # Copie des jetons du joueur
            jetons_joueur = self.jetons.copy()
            total_jetons_jaunes_disponibles = jetons_joueur.get('jaune', 0)
            jaune_utilises = 0
            jetons_utilises = {}

            # Vérifier si le joueur a suffisamment de jetons pour chaque couleur
            for couleur, quantite_necessaire in cout_apres_bonus.items():
                jetons_disponibles = jetons_joueur.get(couleur, 0)
                if jetons_disponibles >= quantite_necessaire:
                    # Le joueur a assez de jetons de cette couleur
                    jetons_utilises[couleur] = quantite_necessaire
                    jetons_joueur[couleur] -= quantite_necessaire
                else:
                    # Le joueur n'a pas assez de jetons de cette couleur
                    quantite_a_completer = quantite_necessaire - jetons_disponibles
                    # Utiliser tous les jetons de couleur restants
                    jetons_utilises[couleur] = jetons_disponibles
                    jetons_joueur[couleur] = 0
                    # Utiliser des jetons jaunes pour compléter
                    if total_jetons_jaunes_disponibles >= quantite_a_completer:
                        jaune_utilises += quantite_a_completer
                        total_jetons_jaunes_disponibles -= quantite_a_completer
                    else:
                        # Pas assez de jetons jaunes pour compléter
                        raise ValueError("Vous n'avez pas assez de jetons pour acheter cette carte.")

            # Retirer les jetons utilisés du joueur
            for couleur, quantite_utilisee in jetons_utilises.items():
                if quantite_utilisee > 0:
                    self.jetons[couleur] -= quantite_utilisee
                    if self.jetons[couleur] == 0:
                        del self.jetons[couleur]

            # Retirer les jetons jaunes utilisés du joueur
            if jaune_utilises > 0:
                self.jetons['jaune'] -= jaune_utilises
                if self.jetons['jaune'] == 0:
                    del self.jetons['jaune']

            self.save()
            print("Jetons du joueur après l'achat :", self.jetons)


            # Ajouter les jetons utilisés au plateau
            for couleur, quantite_utilisee in jetons_utilises.items():
                if quantite_utilisee > 0:
                    plateau_jeton = plateau.jetons.get(couleur=couleur)
                    plateau_jeton.quantite += quantite_utilisee
                    # Assurer que la quantité ne dépasse pas le maximum autorisé
                    plateau_jeton.quantite = min(plateau_jeton.quantite, plateau_jeton.max_quantite)
                    plateau_jeton.save()

            # Ajouter les jetons jaunes utilisés au plateau
            if jaune_utilises > 0:
                plateau_jeton_jaune = plateau.jetons.get(couleur='jaune')
                plateau_jeton_jaune.quantite += jaune_utilises
                # Assurer que la quantité ne dépasse pas le maximum autorisé
                plateau_jeton_jaune.quantite = min(plateau_jeton_jaune.quantite, plateau_jeton_jaune.max_quantite)
                plateau_jeton_jaune.save()

            # Ajouter la carte aux cartes achetées
            self.cartes_achetees.add(carte)
            self.points_victoire += carte.points_victoire

            # Incrémenter le bonus de la couleur de la carte achetée
            couleur_bonus = carte.bonus
            if couleur_bonus in self.bonus:
                self.bonus[couleur_bonus] += 1
            else:
                self.bonus[couleur_bonus] = 1

            self.save()

    def acheter_carte_reservee(self, carte, plateau):
        # Vérifier si la carte est bien réservée par le joueur
        if carte not in self.cartes_reservees.all():
            raise ValueError("La carte sélectionnée n'est pas réservée.")

        # Calculer le coût après application des bonus
        cout_apres_bonus = {}
        for couleur, quantite in carte.cout.items():
            bonus_couleur = self.bonus.get(couleur, 0)
            cout_reduit = max(0, quantite - bonus_couleur)
            cout_apres_bonus[couleur] = cout_reduit

        # Préparer la copie des jetons et la gestion des jetons jaunes
        jetons_joueur = self.jetons.copy()
        total_jetons_jaunes_disponibles = jetons_joueur.get('jaune', 0)
        jaune_utilises = 0
        jetons_utilises = {}

        # Vérifier si le joueur peut couvrir le coût pour chaque couleur
        for couleur, quantite_necessaire in cout_apres_bonus.items():
            jetons_disponibles = jetons_joueur.get(couleur, 0)
            if jetons_disponibles >= quantite_necessaire:
                # Assez de jetons pour cette couleur
                jetons_utilises[couleur] = quantite_necessaire
                jetons_joueur[couleur] -= quantite_necessaire
            else:
                # Pas assez de jetons, utilisation des jetons jaunes
                quantite_a_completer = quantite_necessaire - jetons_disponibles
                jetons_utilises[couleur] = jetons_disponibles
                jetons_joueur[couleur] = 0
                if total_jetons_jaunes_disponibles >= quantite_a_completer:
                    jaune_utilises += quantite_a_completer
                    total_jetons_jaunes_disponibles -= quantite_a_completer
                else:
                    raise ValueError("Vous n'avez pas assez de jetons pour acheter cette carte.")

        # Déduire les jetons du joueur
        for couleur, quantite_utilisee in jetons_utilises.items():
            if quantite_utilisee > 0:
                self.jetons[couleur] -= quantite_utilisee
                if self.jetons[couleur] == 0:
                    del self.jetons[couleur]

        # Retirer les jetons jaunes utilisés du joueur
        if jaune_utilises > 0:
            self.jetons['jaune'] -= jaune_utilises
            if self.jetons['jaune'] == 0:
                del self.jetons['jaune']

        # Sauvegarder les changements de jetons
        self.save()

        # Ajouter les jetons utilisés au plateau
        for couleur, quantite_utilisee in jetons_utilises.items():
            if quantite_utilisee > 0:
                plateau_jeton = plateau.jetons.get(couleur=couleur)
                plateau_jeton.quantite += quantite_utilisee
                plateau_jeton.quantite = min(plateau_jeton.quantite, plateau_jeton.max_quantite)
                plateau_jeton.save()

        # Ajouter les jetons jaunes utilisés au plateau
        if jaune_utilises > 0:
            plateau_jeton_jaune = plateau.jetons.get(couleur='jaune')
            plateau_jeton_jaune.quantite += jaune_utilises
            plateau_jeton_jaune.quantite = min(plateau_jeton_jaune.quantite, plateau_jeton_jaune.max_quantite)
            plateau_jeton_jaune.save()

        # Retirer la carte des réserves et l'ajouter aux cartes achetées
        self.cartes_reservees.remove(carte)
        self.cartes_achetees.add(carte)
        self.points_victoire += carte.points_victoire

        # Incrémenter le bonus pour la couleur de la carte achetée
        couleur_bonus = carte.bonus
        if couleur_bonus in self.bonus:
            self.bonus[couleur_bonus] += 1
        else:
            self.bonus[couleur_bonus] = 1

        # Sauvegarder les changements finaux
        self.save()

            
    def reserver_carte(self, carte, plateau):
        # Vérifier que le joueur n'a pas déjà 3 cartes réservées
        if self.cartes_reservees.count() >= 3:
            raise ValueError("Vous ne pouvez pas avoir plus de 3 cartes réservées.")

        # Ajouter la carte aux cartes réservées
        self.cartes_reservees.add(carte)

        # Vérifier la disponibilité des jetons jaunes sur le plateau
        jeton_jaune = plateau.jetons.filter(couleur='jaune').first()
        if jeton_jaune and jeton_jaune.quantite > 0:
            # Ajouter un jeton jaune au joueur et décrémenter la quantité sur le plateau
            self.jetons['jaune'] = self.jetons.get('jaune', 0) + 1
            jeton_jaune.quantite -= 1
            jeton_jaune.save()
        
        self.save()
