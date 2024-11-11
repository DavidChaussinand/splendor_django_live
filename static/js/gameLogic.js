// gameLogic.js

import { afficherMessage, updateActionButtons, updateBoardAndPlayerTokensMultiple, updateBoardAndPlayerTokensSingle, updateCurrentPlayer ,updateCartesDisplay,updatePlayerPoints ,updateCartesAchetees ,updateCartesReservees, updatePlateauJetons, updatePlayerTokens, refreshPlayerTokens,updatePlayerBonus,updateNoblesAcquis} from './ui.js';
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

         // Gestionnaire d'événements pour acheter une carte réservée
        this.attachReservedCardListeners();
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
    
        if (data.type === "discard_tokens") {
            this.showDiscardTokensModal(data.tokens_to_discard, data.jetons);
        }


        if (data.type === "choose_noble") {
            this.showChooseNobleModal(data.nobles);
        }
    
        if (data.type === "noble_acquired") {
            console.log('Message "noble_acquired" reçu:', data);
            afficherMessage('info', data.message);
            updatePlayerPoints(data.joueur, data.points_victoire);
            this.removeNobleFromBoard(data.noble.id);
            updateNoblesAcquis(data.nobles_acquis); // Pour mettre à jour la liste des nobles acquis si nécessaire
        }


    
        if (data.type === "game_update") {
            if (["acheter_carte", "reserver_carte", "prendre_2_jetons", "prendre_3_jetons", "defausser_jetons", "acheter_carte_reservee"].includes(data.action)) {
                
                // Mise à jour des cartes du plateau si nécessaire
                if (data.cartes) {
                    updateCartesDisplay(data.cartes, data.piles_counts, this);
                }
                
    
                // Mise à jour des jetons du joueur
                updatePlayerTokens(data.joueur, data.jetons);
    
                // Mise à jour des jetons du plateau
                updatePlateauJetons(data.plateau_jetons);
    
                if (data.action === "reserver_carte") {
                    updateCartesReservees(data.joueur, data.cartes_reservees);
                    if (data.joueur === this.monNomUtilisateur) {
                        this.attachReservedCardListeners();
                    }
                }
    
                if (data.action === "acheter_carte") {
                    updatePlayerBonus(data.joueur, data.bonus);
                    updatePlayerPoints(data.joueur, data.points_victoire);
                    updateCartesAchetees(data.joueur, data.cartes_achetees);
                    if (data.joueur === this.monNomUtilisateur) {
                        window.cartesAchetees = data.cartes_achetees;
                    }
                    refreshPlayerTokens(data.joueur, data.jetons);
                    // Mise à jour des nobles acquis
                    updateNoblesAcquis(data.nobles_acquis);
                }
    
                if (data.action === "acheter_carte_reservee") {
                    // Mise à jour des cartes achetées et réservées pour les cartes réservées achetées
                    updateCartesAchetees(data.joueur, data.cartes_achetees);
                    if (data.joueur === this.monNomUtilisateur) {
                        window.cartesAchetees = data.cartes_achetees;
                    }
                    updateCartesReservees(data.joueur, data.cartes_reservees);
                    updatePlayerTokens(data.joueur, data.jetons);
                    updatePlateauJetons(data.plateau_jetons);
                    updatePlayerPoints(data.joueur, data.points_victoire);
                    updatePlayerBonus(data.joueur, data.bonus);
                    // Réattacher les gestionnaires d'événements si c'est le joueur courant
                    if (data.joueur === this.monNomUtilisateur) {
                        this.attachReservedCardListeners();
                    }
                    // Mise à jour des nobles acquis
                    updateNoblesAcquis(data.nobles_acquis);
                }
    
                if (data.action === "defausser_jetons") {
                    afficherMessage('info', `${data.joueur} a défaussé des jetons.`);
                }
                
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

    acheterCarteReservee(carteId) {
        console.log(`Envoi de l'action 'acheter_carte_reservee' pour la carte ID ${carteId}`);
        this.socketClient.send({
            "action": "acheter_carte_reservee",
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

    // gameLogic.js

    showDiscardTokensModal(tokensToDiscard, playerTokens) {
        // Obtenez l'élément modal
        const modal = document.getElementById('discardTokensModal');
        const modalBody = modal.querySelector('.modal-body');
        modalBody.innerHTML = '';

        const tokenSelectors = {};
        const colors = Object.keys(playerTokens);

        colors.forEach(color => {
            const maxQuantity = playerTokens[color];
            const container = document.createElement('div');
            container.classList.add('token-discard');

            const label = document.createElement('label');
            label.textContent = `${color.charAt(0).toUpperCase() + color.slice(1)} (${maxQuantity})`;

            const input = document.createElement('input');
            input.type = 'number';
            input.min = 0;
            input.max = maxQuantity;
            input.value = 0;
            input.dataset.color = color;
            input.addEventListener('change', updateTotalDiscarded.bind(this));

            container.appendChild(label);
            container.appendChild(input);

            modalBody.appendChild(container);

            tokenSelectors[color] = input;
        });

        const totalDiscardedDisplay = document.createElement('p');
        totalDiscardedDisplay.id = 'totalDiscardedDisplay';
        totalDiscardedDisplay.textContent = `Total jetons à défausser: 0 / ${tokensToDiscard}`;
        modalBody.appendChild(totalDiscardedDisplay);

        const confirmButton = modal.querySelector('#confirmDiscardButton');
        confirmButton.disabled = true;
        confirmButton.onclick = () => {
            const jetons_a_defausser = {};
            Object.values(tokenSelectors).forEach(input => {
                const color = input.dataset.color;
                const quantity = parseInt(input.value) || 0;
                if (quantity > 0) {
                    jetons_a_defausser[color] = quantity;
                }
            });
            this.socketClient.send({
                "action": "defausser_jetons",
                "jetons_a_defausser": jetons_a_defausser,
            });
            $(modal).modal('hide');
        };

        function updateTotalDiscarded() {
            let totalDiscarded = 0;
            Object.values(tokenSelectors).forEach(input => {
                totalDiscarded += parseInt(input.value) || 0;
            });
            totalDiscardedDisplay.textContent = `Total jetons à défausser: ${totalDiscarded} / ${tokensToDiscard}`;
            confirmButton.disabled = (totalDiscarded !== tokensToDiscard);
        }

        $(modal).modal('show');
    }

    attachReservedCardListeners() {
        document.querySelectorAll(`[data-username="${this.monNomUtilisateur}"] .carte-img`).forEach(carte => {
            carte.addEventListener("click", (event) => {
                const carteId = event.target.getAttribute("data-id");
                console.log(`Carte réservée cliquée avec l'ID ${carteId}`);
                this.acheterCarteReservee(carteId);
            });
        });
    }



    removeNobleFromBoard(nobleId) {
        console.log('Tentative de suppression du noble avec ID:', nobleId);
        const nobleElement = document.querySelector(`.noble[data-id="${nobleId}"]`);
        if (nobleElement) {
            nobleElement.remove();
            console.log('Élément du noble supprimé:', nobleElement);
        } else {
            console.error('Élément du noble non trouvé avec data-id:', nobleId);
        }
    }


    showChooseNobleModal(nobles) {
        const modal = document.getElementById('chooseNobleModal');
        const modalBody = modal.querySelector('.modal-body');
        modalBody.innerHTML = '';
    
        nobles.forEach(noble => {
            const nobleDiv = document.createElement('div');
            nobleDiv.classList.add('noble-choice');
            nobleDiv.innerHTML = `
                <img src="/static/${noble.image_path}" alt="${noble.nom}">
                <p>${noble.nom}</p>
                <button class="btn btn-primary choose-noble-btn" data-id="${noble.id}">Choisir</button>
            `;
            modalBody.appendChild(nobleDiv);
        });
    
        modal.querySelectorAll('.choose-noble-btn').forEach(button => {
            button.addEventListener('click', () => {
                const nobleId = button.getAttribute('data-id');
                this.socketClient.send({
                    "action": "choisir_noble",
                    "noble_id": nobleId
                });
                $(modal).modal('hide');
            });
        });
    
        $(modal).modal('show');
    }
    
    updateNoblesAcquis(nobles) {
        const noblesList = document.getElementById('nobles-acquis-list');
        noblesList.innerHTML = '';
    
        if (nobles.length > 0) {
            nobles.forEach(noble => {
                const nobleItem = document.createElement('li');
                nobleItem.innerHTML = `
                    <img src="/static/${noble.image_path}" alt="${noble.nom}" class="noble-img">
                    <p>${noble.nom} - ${noble.points_de_victoire} points</p>
                `;
                noblesList.appendChild(nobleItem);
            });
        } else {
            noblesList.innerHTML = '<p>Aucun noble acquis pour le moment</p>';
        }
    }
    
    
}
