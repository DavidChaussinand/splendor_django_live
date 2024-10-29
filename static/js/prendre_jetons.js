class Jeu {
    constructor() {
        this.selectedColors = new Set();
        this.gameSocket = null;
        this.monNomUtilisateur = monNomUtilisateur;
        this.currentPlayer = currentPlayer;

        this.initWebSocket();
        this.initEventListeners();
        this.updateActionButtons(this.currentPlayer === this.monNomUtilisateur);
    }

    // Initialisation de la connexion WebSocket
    initWebSocket() {
        this.gameSocket = new WebSocket(
            "ws://" + window.location.host + "/ws/game/" + nom_partie + "/"
        );

        this.gameSocket.onmessage = this.handleSocketMessage.bind(this);
        this.gameSocket.onclose = this.handleSocketClose.bind(this);
    }

    // Initialisation des gestionnaires d'événements
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
    }

    // Mise à jour des boutons d'action en fonction du tour
    updateActionButtons(isMyTurn) {
        const prendreDeuxJetonsButton = document.getElementById("prendre-deux-jetons");
        const prendreTroisJetonsButton = document.getElementById("prendre-trois-jetons");

        if (prendreDeuxJetonsButton) prendreDeuxJetonsButton.disabled = !isMyTurn;
        if (prendreTroisJetonsButton) prendreTroisJetonsButton.disabled = !isMyTurn;
    }

    // Afficher un message dans le conteneur
    afficherMessage(type, texte) {
        const messageContainer = document.getElementById('message-container');
        if (!messageContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('alert', `alert-${type === 'error' ? 'danger' : 'success'}`);
        messageDiv.textContent = texte;
        messageContainer.appendChild(messageDiv);

        setTimeout(() => messageContainer.removeChild(messageDiv), 2000);
    }

    // Gestion des messages reçus du serveur
    handleSocketMessage(e) {
        const data = JSON.parse(e.data);
        console.log('Données reçues :', data);

        if (data.error) {
            this.afficherMessage('error', data.error);
            return;
        }

        if (data.message) {
            this.afficherMessage('info', data.message);

            // Mise à jour du plateau et des jetons du joueur
            if (data.couleurs) {
                this.updateBoardAndPlayerTokensMultiple(data);
            } else if (data.couleur) {
                this.updateBoardAndPlayerTokensSingle(data);
            }
        }

        // Mise à jour du joueur courant
        if (data.type === "tour_update") {
            console.log("Message 'tour_update' reçu :", data);
            const joueurTourElement = document.getElementById("current_player");
            if (joueurTourElement) {
                joueurTourElement.innerText = "C'est au tour de : " + data.current_player;
            }

            // Vérifier si c'est le tour de l'utilisateur actuel
            const isMyTurn = data.current_player === this.monNomUtilisateur;
            console.log("Est-ce mon tour ? ", isMyTurn);
            this.updateActionButtons(isMyTurn);
        }
    }

    // Gestion de la fermeture de la connexion WebSocket
    handleSocketClose() {
        console.error("Socket fermé de manière inattendue.");
    }

    // Mise à jour du plateau et des jetons du joueur pour plusieurs couleurs
    updateBoardAndPlayerTokensMultiple(data) {
        data.couleurs.forEach(couleur => {
            // Mise à jour du plateau
            const plateauJetonElement = document.querySelector(`#plateau-${couleur}-quantite span`);
            if (plateauJetonElement) {
                plateauJetonElement.innerText = parseInt(plateauJetonElement.innerText) - 1;
            }

            // Mise à jour des jetons du joueur concerné
            if (data.joueur) {
                const joueurJetonElement = document.querySelector(`#joueur-jetons-${data.joueur}-${couleur} span`);
                if (joueurJetonElement) {
                    joueurJetonElement.innerText = parseInt(joueurJetonElement.innerText) + 1;
                }
            }
        });
    }

    // Mise à jour du plateau et des jetons du joueur pour une seule couleur
    updateBoardAndPlayerTokensSingle(data) {
        const plateauJetonElement = document.querySelector(`#plateau-${data.couleur}-quantite span`);
        if (plateauJetonElement) {
            plateauJetonElement.innerText = data.quantite_restant;
        }

        // Mise à jour des jetons du joueur concerné
        if (data.joueur) {
            const joueurJetonElement = document.querySelector(`#joueur-jetons-${data.joueur}-${data.couleur} span`);
            if (joueurJetonElement) {
                joueurJetonElement.innerText = parseInt(joueurJetonElement.innerText) + 2;
            }
        }
    }

    // Gestion de la sélection des jetons
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

    // Fonction pour envoyer la demande de prise de deux jetons
    prendre2Jetons() {
        if (this.selectedColors.size !== 1) {
            this.afficherMessage('error', "Veuillez sélectionner une seule couleur.");
            return;
        }

        const couleur = Array.from(this.selectedColors)[0];
        this.gameSocket.send(JSON.stringify({
            "action": "prendre_2_jetons",
            "couleur": couleur
        }));

        this.resetSelection();
    }

    // Fonction pour envoyer la demande de prise de trois jetons différents
    prendre3Jetons() {
        if (this.selectedColors.size !== 3) {
            this.afficherMessage('error', "Veuillez sélectionner trois couleurs différentes.");
            return;
        }

        const couleurs = Array.from(this.selectedColors);
        this.gameSocket.send(JSON.stringify({
            "action": "prendre_3_jetons",
            "couleurs": couleurs
        }));

        this.resetSelection();
    }

    // Réinitialiser la sélection
    resetSelection() {
        this.selectedColors.clear();
        document.querySelectorAll(".jeton").forEach(j => j.classList.remove("selected"));
    }
}

// Instancier la classe Jeu lorsque le DOM est chargé
document.addEventListener("DOMContentLoaded", function () {
    new Jeu();
});
