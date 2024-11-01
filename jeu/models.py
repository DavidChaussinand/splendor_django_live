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
    cartes = models.ManyToManyField(Carte, related_name='plateaux')

    def __str__(self):
        return f"Plateau de la partie {self.partie.nom}"



class Jeton(models.Model):
    couleur = models.CharField(max_length=50)
    quantite = models.PositiveIntegerField()
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
        
    def acheter_carte(self, carte):
        self.cartes_achetees.add(carte)  # Ajoute la carte à la liste des cartes achetées
        self.points_victoire += carte.points_victoire  # Incrémente les points de victoire du joueur
        # Incrémenter le bonus de la couleur de la carte achetée
        couleur_bonus = carte.bonus  # Supposons que carte.bonus est une chaîne représentant la couleur
        if couleur_bonus in self.bonus:
            self.bonus[couleur_bonus] += 1
        else:
            self.bonus[couleur_bonus] = 1
        self.save()  # 