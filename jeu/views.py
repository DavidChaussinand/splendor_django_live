# jeu/views.py


from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EmailAuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm
from .models import  Jeton , Partie , Plateau , JoueurPartie ,Carte
from .utils import generer_plateau
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from random import sample 
import random


from django.http import JsonResponse

def home(request):
    return render(request, 'jeu_templates/home.html')


def user_login(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirige vers la page d'accueil
            else:
                messages.error(request, 'Email ou mot de passe incorrect')
    else:
        form = EmailAuthenticationForm()
    
    return render(request, 'jeu_templates/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')  # Redirige vers la page d'accueil après déconnexion


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Votre compte a été créé avec succès.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'jeu_templates/register.html', {'form': form})

def game_view(request, nombre_joueurs=2):
    joueur_courant_id = request.session.get("joueur_id")
    print("ID du joueur dans la session :", joueur_courant_id)  # Vérifie si joueur_id est défini

    if not joueur_courant_id:
        print("Redirection vers login - joueur_id absent de la session.")
        return redirect('login')

    joueur_courant = get_object_or_404(Joueur, id=joueur_courant_id)
    print("Joueur courant récupéré :", joueur_courant.nom)
    
    # Sélectionne un adversaire (supposé être un autre joueur)
    adversaire = Joueur.objects.exclude(id=joueur_courant_id).first()

    # Récupérer les jetons du joueur courant depuis la session ou initialiser
    joueur_courant_jetons = request.session.get('joueur_courant_jetons', {color: 0 for color in ["noir","bleue", "blanc", "rouge", "vert", "jaune"]})
    # Idem pour l'adversaire si nécessaire

    # Générer le plateau ou le récupérer depuis la session
    plateau = request.session.get('plateau')
    if not plateau:
        plateau = generer_plateau(nombre_joueurs)
        request.session['plateau'] = plateau

    context = {
        "joueur_courant": joueur_courant,
        "adversaire": adversaire,
        "joueur_courant_jetons": joueur_courant_jetons,
        "plateau": plateau
    }

    return render(request, 'jeu_templates/game.html', context)


def login_view(request):
    if request.method == "POST":
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                print("Connexion réussie pour :", user.username)
                
                # Supprime la logique liée à Joueur et redirige directement
                return redirect("home")
            else:
                print("Échec de l'authentification - utilisateur est None")
                messages.error(request, 'Nom d’utilisateur ou mot de passe incorrect')
        else:
            print("Erreurs du formulaire :", form.errors)
    else:
        form = EmailAuthenticationForm()
    
    return render(request, 'jeu_templates/login.html', {'form': form})



# --------------------------------- action joueur ----------------------------------------
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # N'oublie pas de gérer correctement le CSRF en production
def prendre_2_jetons_de_meme_couleur(request):
    if request.method == "POST":
        couleur = request.POST.get("couleur")
        joueur_id = request.session.get("joueur_id")

        if not couleur or not joueur_id:
            return JsonResponse({"success": False, "error": "Données invalides"})

        # Récupérer le plateau depuis la session
        plateau = request.session.get('plateau')
        if not plateau:
            return JsonResponse({"success": False, "error": "Plateau introuvable dans la session."})

        # Vérifier la disponibilité des jetons
        quantite_disponible = plateau.get(couleur, 0)
        if quantite_disponible >= 4:
            if quantite_disponible >= 2:
                # Mettre à jour le plateau
                plateau[couleur] -= 2
                request.session['plateau'] = plateau

                # Mettre à jour les jetons du joueur
                joueur_jetons = request.session.get('joueur_courant_jetons', {color: 0 for color in ["noir", "blanc", "rouge", "vert", "jaune"]})
                joueur_jetons[couleur] += 2
                request.session['joueur_courant_jetons'] = joueur_jetons

                return JsonResponse({"success": True, "message": f"Le joueur a pris 2 jetons {couleur}."})
            else:
                return JsonResponse({"success": False, "error": f"Pas assez de jetons {couleur} pour en prendre 2."})
        else:
            return JsonResponse({"success": False, "error": f"Il faut au moins 4 jetons {couleur} sur le plateau pour prendre 2."})
    return JsonResponse({"success": False, "error": "Requête non valide"})




def reset_game(request, partie_id):
    try:
        # Récupérer la partie en fonction de l'ID
        partie = get_object_or_404(Partie, id=partie_id)
        
        # Réinitialiser le plateau
        plateau = partie.plateau
        nombre_joueurs = partie.nombre_joueurs
        
        # Quantité de jetons par couleur en fonction du nombre de joueurs
        couleurs_quantites = (
            {"noir": 4,"bleu": 4, "blanc": 4, "rouge": 4, "vert": 4, "jaune": 5} if nombre_joueurs == 2 else
            {"noir": 5,"bleu": 5,"blanc": 5, "rouge": 5, "vert": 5, "jaune": 5} if nombre_joueurs == 3 else
            {"noir": 7,"bleu": 7,"blanc": 7, "rouge": 7, "vert": 7, "jaune": 5}
        )

        # Mettre à jour les quantités de jetons sur le plateau
        for couleur, quantite in couleurs_quantites.items():
            jeton, created = Jeton.objects.get_or_create(plateau=plateau, couleur=couleur)
            jeton.quantite = quantite
            jeton.save()

        # Réinitialiser les données pour chaque joueur
        joueurs = JoueurPartie.objects.filter(partie=partie)
        for joueur in joueurs:
            joueur.points_victoire = 0
            joueur.jetons = {"noir": 0, "bleu": 0, "blanc": 0, "rouge": 0, "vert": 0, "jaune": 0}
            joueur.bonus = {} 
            joueur.cartes_achetees.clear()
            joueur.cartes_reservees.clear()
            joueur.save()

        # Après avoir défini `joueur_jetons`
        

        # Logique de réinitialisation des cartes aléatoires
        # Supposons que vous souhaitiez afficher 4 cartes au hasard pour chaque niveau
        # Sélectionner aléatoirement des cartes pour le plateau (comme dans creer_partie)
        plateau.cartes.clear()
        cartes_plateau = []

        # Construire la réponse JSON avec l’état réinitialisé
        for niveau in [1, 2, 3]:
            cartes_niveau = list(Carte.objects.filter(niveau=niveau))
            cartes_selectionnees = random.sample(cartes_niveau, min(4, len(cartes_niveau)))
            cartes_plateau.extend(cartes_selectionnees)

        plateau.cartes.set(cartes_plateau)
        plateau.save()

        # Construire la réponse JSON avec l’état réinitialisé
        plateau_jetons = {jeton.couleur: jeton.quantite for jeton in plateau.jetons.all()}
        joueur_jetons = {joueur.joueur.username: joueur.jetons for joueur in joueurs}
        joueur_bonus = {joueur.joueur.username: joueur.bonus for joueur in joueurs}
        cartes_infos = [
            {
                "id": carte.id,
                "niveau": carte.niveau,
                "cout": carte.cout,
                "bonus": carte.bonus,
                "points_victoire": carte.points_victoire,
                "image": carte.image_path,  # Utilisez l'URL d'image ici
                
            }
            for carte in cartes_plateau
        ]

        return JsonResponse({
            "success": True,
            "message": "La partie a été réinitialisée.",
            "plateau": plateau_jetons,
            "joueurs": joueur_jetons,
            "bonus": joueur_bonus,  # Ajoutez cette ligne
            "cartes": cartes_infos,
        })
    
    except Exception as e:
        # Log de l'erreur pour le débogage
        print("Erreur dans reset_game:", str(e))  # Ou utilisez logging.error("Erreur dans reset_game:", exc_info=True)

        return JsonResponse({
            "success": False,
            "message": "Erreur lors de la réinitialisation de la partie.",
            "error": str(e),
        }, status=500)






class CreerPartieView(LoginRequiredMixin, View):
    def get(self, request):
        parties = Partie.objects.all()
        return render(request, 'jeu_templates/creer_partie.html', {'parties': parties})

    def post(self, request):
        nom_partie = request.POST.get('nom_partie')
        nombre_joueurs = int(request.POST.get('nombre_joueurs'))

        # Vérifier si le nom de la partie existe déjà
        if Partie.objects.filter(nom=nom_partie).exists():
            erreur = "Une partie avec ce nom existe déjà."
            parties = Partie.objects.all()
            return render(request, 'jeu_templates/creer_partie.html', {'erreur': erreur, 'parties': parties})

        partie = Partie.objects.create(nom=nom_partie, nombre_joueurs=nombre_joueurs, joueur_courant=request.user)
        partie.joueurs.add(request.user)
        JoueurPartie.objects.create(joueur=request.user, partie=partie, jetons={"noir": 0, "bleu": 0, "blanc": 0, "rouge": 0, "vert": 0, "jaune": 0})

        # Créer le plateau associé à la partie
        plateau = Plateau.objects.create(partie=partie)

        # Initialiser les jetons en fonction du nombre de joueurs
        couleurs_quantites = {
            2: {"noir": 4, "bleu": 4, "blanc": 4, "rouge": 4, "vert": 4, "jaune": 5},
            3: {"noir": 5, "bleu": 5, "blanc": 5, "rouge": 5, "vert": 5, "jaune": 5},
            4: {"noir": 7, "bleu": 7, "blanc": 7, "rouge": 7, "vert": 7, "jaune": 5},
        }.get(nombre_joueurs, {})

        for couleur, quantite in couleurs_quantites.items():
            Jeton.objects.create(couleur=couleur, quantite=quantite, plateau=plateau)

        # Pile et affichage sur le plateau pour chaque niveau de carte
        for niveau in [1, 2, 3]:
            toutes_les_cartes_niveau = list(Carte.objects.filter(niveau=niveau))
            cartes_pile_niveau = sample(toutes_les_cartes_niveau, len(toutes_les_cartes_niveau))

            # Ajoute les 4 premières cartes de chaque niveau au plateau
            plateau.cartes.add(*cartes_pile_niveau[:4])

            # Ajoute le reste des cartes dans les piles correspondantes
            if niveau == 1:
                plateau.cartes_pile_niveau_1.set(cartes_pile_niveau[4:])
            elif niveau == 2:
                plateau.cartes_pile_niveau_2.set(cartes_pile_niveau[4:])
            elif niveau == 3:
                plateau.cartes_pile_niveau_3.set(cartes_pile_niveau[4:])

        message = "La partie a été créée avec succès."
        parties = Partie.objects.all()
        return render(request, 'jeu_templates/creer_partie.html', {
            'message': message,
            'parties': parties,
        })

class GameView(LoginRequiredMixin, View):
    def get(self, request, nom_partie):
        partie = get_object_or_404(Partie, nom=nom_partie)

        if request.user not in partie.joueurs.all():
            return redirect('creer_partie')

        joueur_courant, created = JoueurPartie.objects.get_or_create(
            joueur=request.user,
            partie=partie,
            defaults={'points_victoire': 0, 'jetons': {"noir": 0, "bleu": 0, "blanc": 0, "rouge": 0, "vert": 0, "jaune": 0}}
        )

        plateau = partie.plateau
        jetons = plateau.jetons.all()
        plateau_jetons = {jeton.couleur: jeton.quantite for jeton in jetons}
        # Cartes visibles par niveau
        cartes_plateau_niveau_1 = plateau.cartes.filter(niveau=1)
        cartes_plateau_niveau_2 = plateau.cartes.filter(niveau=2)
        cartes_plateau_niveau_3 = plateau.cartes.filter(niveau=3)

        
        cartes_pile_niveau_1 = plateau.cartes_pile_niveau_1.all()  # Récupérer les cartes de la pile de niveau 1
        cartes_pile_niveau_2 = plateau.cartes_pile_niveau_2.all()
        cartes_pile_niveau_3 = plateau.cartes_pile_niveau_3.all()

        # Obtenir les adversaires et convertir leurs cartes réservées en listes
        # Obtenir les adversaires et les cartes réservées comme liste
        adversaires = JoueurPartie.objects.filter(partie=partie).exclude(joueur=request.user)
        for adversaire in adversaires:
            adversaire.cartes_reservees_list = list(adversaire.cartes_reservees.all())  # Convertir en liste pour le template

        current_player = partie.joueur_courant
        cartes_achetees = [{
            'id': carte.id,
            'image_path': carte.image_path,
            'niveau': carte.niveau
        } for carte in joueur_courant.cartes_achetees.all()]

        context = {
            'nom_partie': partie.nom,
            'partie': partie,
            'joueur_courant': joueur_courant,
            'adversaires': adversaires,
            'plateau': plateau_jetons,
            'cartes_plateau_niveau_1': cartes_plateau_niveau_1,
            'cartes_plateau_niveau_2': cartes_plateau_niveau_2,
            'cartes_plateau_niveau_3': cartes_plateau_niveau_3,
            'cartes_pile_niveau_1': cartes_pile_niveau_1,  # Ajouter cette variable pour le template
            'cartes_pile_niveau_2': cartes_pile_niveau_2,
            'cartes_pile_niveau_3': cartes_pile_niveau_3,
            'current_player': current_player,
            'cartes_achetees': cartes_achetees,
            'is_game_page': True,
        }
        return render(request, 'jeu_templates/game.html', context)


    
class RejoindrePartieView(LoginRequiredMixin, View):
    def post(self, request, partie_id):
        partie = get_object_or_404(Partie, id=partie_id)

        # Vérifier si la partie est complète
        if partie.joueurs.count() >= partie.nombre_joueurs:
            parties = Partie.objects.all()
            erreur = "Cette partie est déjà complète."
            return render(request, 'jeu_templates/creer_partie.html', {'erreur': erreur, 'parties': parties})

        # Ajouter l'utilisateur à la partie s'il n'est pas déjà dedans
        if request.user not in partie.joueurs.all():
            partie.joueurs.add(request.user)
            partie.save()

            # Vérifier si une entrée JoueurPartie existe, sinon la créer
            JoueurPartie.objects.get_or_create(
                joueur=request.user,
                partie=partie,
                defaults={'points_victoire': 0, 'jetons': {"noir": 0,"bleu":0, "blanc": 0, "rouge": 0, "vert": 0, "jaune": 0}}
            )

        return redirect('game_view', nom_partie=partie.nom)


    


