// gameLogic.js

import { afficherMessage, updateActionButtons, updateBoardAndPlayerTokensMultiple, updateBoardAndPlayerTokensSingle, updateCurrentPlayer ,updateCartesDisplay,updatePlayerPoints ,updateCartesAchetees ,updateCartesReservees, updatePlateauJetons, updatePlayerTokens, refreshPlayerTokens} from './ui.js';
import { WebSocketClient } from './websocket.js';

export class Game {
    constructor(nom_partie, monNomUtilisateur, currentPlayer) {
        this.nom_partie = nom_partie;
        this.monNomUtilisateur = monNomUtilisateur;
        this.currentPlayer = currentPlayer;
        this.selectedColors = new Set();

        this.initWebSocket();
        this.initEventListeners();
        this.updateActionButtons(this.currentPlayer === this.monNomUtilisateur);
    }

    initWebSocket() {
        const url = "ws://" + window.location.host + "/ws/game/" + this.nom_partie + "/";
        this.socketClient = new WebSocketClient(url, this.handleSocketMessage.bind(this), this.handleSocketClose.bind(this));
    }

    initEventListeners() {
        // Gestionnaires d'événements pour les boutons
        const prendreDeuxJetonsButton = document.getElementById("prendre-deux-jetons");
        if (prendreDeuxJetonsButton) {
            prendreDeuxJetonsButton.addEventListener("click", this.prendre2Jetons.bind(this));
        }

        const prendreTroisJetonsButton = document.getElementById("prendre-trois-jetons");
        if (prendreTroisJetonsButton) {
            prendreTroisJetonsButton.addEventListener("click", this.prendre3Jetons.bind(this));
        }

        // Gestionnaires d'événements pour la sélection des jetons
        document.querySelectorAll(".jeton").forEach(jeton => {
            jeton.addEventListener("click", this.handleJetonClick.bind(this));
        });

        // **NOUVEAU** : Gestionnaires d'événements pour les cartes
        document.querySelectorAll(".carte").forEach(carte => {
            carte.addEventListener("click", this.handleCarteClick.bind(this));
        });

        // Gestionnaires d'événements pour les boutons "Réserver"
        document.querySelectorAll(".reserver-carte-btn").forEach(button => {
            button.addEventListener("click", (event) => {
                event.stopPropagation(); // Empêche la propagation vers la carte
                const carteId = button.getAttribute("data-id");
                this.reserverCarte(carteId);
            });
        });
    }

    handleSocketMessage(e) {
        const data = JSON.parse(e.data);
        console.log('Données reçues :', data);
    
        if (data.error) {
            afficherMessage('error', data.error);
            return;
        }
    
        if (data.message) {
            afficherMessage('info', data.message);
        }
    
        if (data.type === "tour_update") {
            console.log("Message 'tour_update' reçu :", data);
            updateCurrentPlayer(data);
    
            const isMyTurn = data.current_player === this.monNomUtilisateur;
            console.log("Est-ce mon tour ? ", isMyTurn);
            updateActionButtons(isMyTurn);
        }
    
        if (data.type === "game_update") {
            if (["acheter_carte", "reserver_carte", "prendre_2_jetons", "prendre_3_jetons"].includes(data.action)) {

                if (data.cartes) {
                    updateCartesDisplay(data.cartes, this);
                }

                // Mise à jour des jetons du joueur
                updatePlayerTokens(data.joueur, data.jetons);
                
                
    
                // Mise à jour des jetons du plateau
                for (const [couleur, quantite] of Object.entries(data.plateau_jetons)) {
                    const plateauJetonElement = document.querySelector(`#plateau-${couleur}-quantite span`);
                    if (plateauJetonElement) {
                        plateauJetonElement.innerText = quantite;
                    }
                }
    
                if (data.action === "reserver_carte") {
                    // Mise à jour des cartes réservées du joueur
                    updateCartesReservees(data.joueur, data.cartes_reservees);
                }
    
                if (data.action === "acheter_carte") {
                    // Mise à jour des bonus du joueur
                    this.updatePlayerBonus(data.joueur, data.bonus);
    
                    // Mise à jour des points de victoire du joueur
                    updatePlayerPoints(data.joueur, data.points_victoire);
    
                    // Mise à jour des cartes achetées du joueur
                    updateCartesAchetees(data.joueur, data.cartes_achetees);
                    // Rafraîchissement visuel des jetons du joueur après l'achat
                    refreshPlayerTokens(data.joueur, data.jetons);
                   
                }
    
                // Vous pouvez ajouter des messages spécifiques pour les actions "prendre_2_jetons" et "prendre_3_jetons" si nécessaire
            }
        }
    }
    


    handleSocketClose() {
        console.error("Socket fermé de manière inattendue.");
    }

    handleJetonClick(event) {
        const jeton = event.target.closest(".jeton");
        if (!jeton) return;

        const color = jeton.getAttribute("data-color");

        if (this.selectedColors.has(color)) {
            this.selectedColors.delete(color);
            jeton.classList.remove("selected");
        } else {
            if (this.selectedColors.size >= 3) {
                // Limite la sélection à 3 couleurs maximum
                const firstSelected = Array.from(this.selectedColors)[0];
                this.selectedColors.delete(firstSelected);
                document.querySelector(`.jeton[data-color="${firstSelected}"]`).classList.remove("selected");
            }
            this.selectedColors.add(color);
            jeton.classList.add("selected");
        }
    }

    prendre2Jetons() {
        if (this.selectedColors.size !== 1) {
            afficherMessage('error', "Veuillez sélectionner une seule couleur.");
            return;
        }

        const couleur = Array.from(this.selectedColors)[0];
        this.socketClient.send({
            "action": "prendre_2_jetons",
            "couleur": couleur
        });

        this.resetSelection();
    }

    prendre3Jetons() {
        if (this.selectedColors.size !== 3) {
            afficherMessage('error', "Veuillez sélectionner trois couleurs différentes.");
            return;
        }

        const couleurs = Array.from(this.selectedColors);
        this.socketClient.send({
            "action": "prendre_3_jetons",
            "couleurs": couleurs
        });

        this.resetSelection();
    }


    handleCarteClick(event) {
        const carteElement = event.currentTarget;
        const carteId = carteElement.getAttribute('data-id');
        this.acheterCarte(carteId);
    }

    handleReserverCarteClick(event) {
        const carteId = event.target.getAttribute('data-id');
        this.reserverCarte(carteId);
    }
    

    updatePlayerBonus(joueur, bonus) {
        for (const [couleur, quantite] of Object.entries(bonus)) {
            const joueurBonusElement = document.querySelector(`#joueur-bonus-${joueur}-${couleur} span`);
            if (joueurBonusElement) {
                joueurBonusElement.innerText = quantite;
            } else {
                // Si l'élément n'existe pas, le créer
                const bonusList = document.querySelector(`#joueur-bonus-list-${joueur}`);
                if (bonusList) {
                    const newBonusItem = document.createElement('li');
                    newBonusItem.id = `joueur-bonus-${joueur}-${couleur}`;
                    newBonusItem.classList.add('m-2');
                    newBonusItem.innerHTML = `<strong>${couleur.charAt(0).toUpperCase() + couleur.slice(1)}</strong> : <span>${quantite}</span>`;
                    bonusList.appendChild(newBonusItem);
                }
            }
        }
    }
    
    acheterCarte(carteId) {
        this.socketClient.send({
            "action": "acheter_carte",
            "carte_id": carteId
        });
    }

    reserverCarte(carteId) {
        this.socketClient.send({
            "action": "reserver_carte",
            "carte_id": carteId
        });
    }
    

    resetSelection() {
        this.selectedColors.clear();
        document.querySelectorAll(".jeton").forEach(j => j.classList.remove("selected"));
    }

    updateActionButtons(isMyTurn) {
        updateActionButtons(isMyTurn);
    }
}
