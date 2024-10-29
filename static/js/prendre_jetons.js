document.addEventListener("DOMContentLoaded", function () {
    let selectedColor = null;
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
        if (prendreDeuxJetonsButton) {
            prendreDeuxJetonsButton.disabled = !isMyTurn;
        }
    }

// Fonction pour gérer la réception des messages du serveur
    gameSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        console.log('Données reçues :', data);

        if (data.error) {
            // Remplacez alert par une notification non bloquante
            Swal.fire({
                icon: 'error',
                title: 'Erreur',
                text: data.error,
            });
            return;
        }

            if (data.message) {
                Swal.fire({
                    icon: 'info',
                    title: 'Information',
                    text: data.message,
                });

                // Mise à jour du plateau
                if (data.couleur) {
                    const plateauJetonElement = document.querySelector(`#plateau-${data.couleur}-quantite span`);
                    if (plateauJetonElement) {
                        plateauJetonElement.innerText = data.quantite_restant;
                    }
                }

                // Mise à jour des jetons du joueur concerné
                if (data.joueur && data.couleur) {
                    const joueurJetonElement = document.querySelector(`#joueur-jetons-${data.joueur}-${data.couleur} span`);
                    if (joueurJetonElement) {
                        joueurJetonElement.innerText = parseInt(joueurJetonElement.innerText) + 2;
                    } else {
                        console.log('Élément joueurJetonElement non trouvé pour :', `#joueur-jetons-${data.joueur}-${data.couleur} span`);
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
                console.log("Est-ce mon tour ? ", isMyTurn);  // Log pour déboguer
                updateActionButtons(isMyTurn);
            }
};

    // Gestion de la fermeture de la connexion WebSocket
    gameSocket.onclose = function () {
        console.error("Socket fermé de manière inattendue.");
    };

    // Fonction pour gérer la sélection d'un jeton
    function handleJetonClick(event) {
        const jeton = event.target.closest(".jeton");
        if (!jeton) return;

        // Enregistrer la couleur sélectionnée
        selectedColor = jeton.getAttribute("data-color");

        // Ajouter un effet visuel pour montrer le jeton sélectionné
        document.querySelectorAll(".jeton").forEach(j => j.classList.remove("selected"));
        jeton.classList.add("selected");
    }

    // Fonction pour envoyer la demande de prise de deux jetons au serveur
    function prendre2Jetons() {
        if (!selectedColor) {
            alert("Veuillez d'abord sélectionner une couleur de jeton.");
            return;
        }

        // Envoyer l'action via WebSocket
        gameSocket.send(JSON.stringify({
            "action": "prendre_2_jetons",
            "couleur": selectedColor
        }));

        // Réinitialiser la sélection
        selectedColor = null;
        document.querySelectorAll(".jeton").forEach(j => j.classList.remove("selected"));
    }

    // Ajout des gestionnaires d'événements pour la sélection des jetons
    document.querySelectorAll(".jeton").forEach(jeton => {
        jeton.addEventListener("click", handleJetonClick);
    });

    // Gestionnaire d'événement pour le bouton "Prendre deux jetons"
    const prendreDeuxJetonsButton = document.getElementById("prendre-deux-jetons");
    if (prendreDeuxJetonsButton) {
        prendreDeuxJetonsButton.addEventListener("click", prendre2Jetons);
    }

    // Désactive le bouton si ce n'est pas le tour de l'utilisateur actuel
    const initialIsMyTurn = currentPlayer === monNomUtilisateur;
    updateActionButtons(initialIsMyTurn);
});
