document.addEventListener("DOMContentLoaded", function () {
    let selectedColors = new Set();
    console.log("Partie ID:", partieId);

    // Afficher les valeurs pour débogage
    console.log('monNomUtilisateur:', monNomUtilisateur);
    console.log('currentPlayer:', currentPlayer);

    // Initialisation de la connexion WebSocket
    const gameSocket = new WebSocket(
        "ws://" + window.location.host + "/ws/game/" + nom_partie + "/"
    );

    // Fonction pour activer/désactiver le bouton en fonction du tour
    function updateActionButtons(isMyTurn) {
        const prendreDeuxJetonsButton = document.getElementById("prendre-deux-jetons");
        const prendreTroisJetonsButton = document.getElementById("prendre-trois-jetons");
        
        if (prendreDeuxJetonsButton) prendreDeuxJetonsButton.disabled = !isMyTurn;
        if (prendreTroisJetonsButton) prendreTroisJetonsButton.disabled = !isMyTurn;
    }

    // Fonction pour afficher un message dans le conteneur
    function afficherMessage(type, texte) {
        const messageContainer = document.getElementById('message-container');
        if (!messageContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.classList.add('alert', `alert-${type === 'error' ? 'danger' : 'success'}`);
        messageDiv.textContent = texte;
        messageContainer.appendChild(messageDiv);

        setTimeout(() => messageContainer.removeChild(messageDiv), 2000);
    }

    // Fonction pour gérer la réception des messages du serveur

    gameSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        console.log('Données reçues :', data);

        if (data.error) {
            afficherMessage('error', data.error);
            return;
        }

        if (data.message) {
            afficherMessage('info', data.message);

            // Mise à jour du plateau et des jetons du joueur
            if (data.couleurs) {
                // Si plusieurs couleurs sont reçues (prise de 3 jetons)
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
            } else if (data.couleur) {
                // Si une seule couleur est reçue (prise de 2 jetons)
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
        }

        // Mise à jour du joueur courant
        if (data.type === "tour_update") {
            console.log("Message 'tour_update' reçu :", data);
            const joueurTourElement = document.getElementById("current_player");
            if (joueurTourElement) {
                joueurTourElement.innerText = "C'est au tour de : " + data.current_player;
            }

            // Vérifier si c'est le tour de l'utilisateur actuel
            const isMyTurn = data.current_player === monNomUtilisateur;
            console.log("Est-ce mon tour ? ", isMyTurn);
            updateActionButtons(isMyTurn);
        }
    };


    // Gestion de la fermeture de la connexion WebSocket
    gameSocket.onclose = function () {
        console.error("Socket fermé de manière inattendue.");
    };

    // Fonction pour gérer la sélection de plusieurs jetons
    function handleJetonClick(event) {
        const jeton = event.target.closest(".jeton");
        if (!jeton) return;

        const color = jeton.getAttribute("data-color");

        if (selectedColors.has(color)) {
            selectedColors.delete(color);
            jeton.classList.remove("selected");
        } else if (selectedColors.size < 3) {
            selectedColors.add(color);
            jeton.classList.add("selected");
        }

        // Limite la sélection à 3 couleurs maximum
        if (selectedColors.size > 3) {
            const firstSelected = Array.from(selectedColors)[0];
            selectedColors.delete(firstSelected);
            document.querySelector(`.jeton[data-color="${firstSelected}"]`).classList.remove("selected");
        }
    }

    // Fonction pour envoyer la demande de prise de deux jetons au serveur
    function prendre2Jetons() {
        if (selectedColors.size !== 1) {
            afficherMessage('error', "Veuillez sélectionner une seule couleur.");
            return;
        }

        const couleur = Array.from(selectedColors)[0];
        gameSocket.send(JSON.stringify({
            "action": "prendre_2_jetons",
            "couleur": couleur
        }));

        selectedColors.clear();
        document.querySelectorAll(".jeton").forEach(j => j.classList.remove("selected"));
    }

    // Fonction pour envoyer la demande de prise de trois jetons différents au serveur
    function prendre3Jetons() {
        if (selectedColors.size !== 3) {
            afficherMessage('error', "Veuillez sélectionner trois couleurs différentes.");
            return;
        }

        const couleurs = Array.from(selectedColors);
        gameSocket.send(JSON.stringify({
            "action": "prendre_3_jetons",
            "couleurs": couleurs
        }));

        selectedColors.clear();
        document.querySelectorAll(".jeton").forEach(j => j.classList.remove("selected"));
    }

    // Ajout des gestionnaires d'événements pour la sélection des jetons
    document.querySelectorAll(".jeton").forEach(jeton => {
        jeton.addEventListener("click", handleJetonClick);
    });

    // Gestionnaires d'événements pour les boutons
    const prendreDeuxJetonsButton = document.getElementById("prendre-deux-jetons");
    if (prendreDeuxJetonsButton) {
        prendreDeuxJetonsButton.addEventListener("click", prendre2Jetons);
    }

    const prendreTroisJetonsButton = document.getElementById("prendre-trois-jetons");
    if (prendreTroisJetonsButton) {
        prendreTroisJetonsButton.addEventListener("click", prendre3Jetons);
    }

    // Désactiver les boutons si ce n'est pas le tour de l'utilisateur actuel
    const initialIsMyTurn = currentPlayer === monNomUtilisateur;
    updateActionButtons(initialIsMyTurn);
});
