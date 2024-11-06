// ui.js

export function afficherMessage(type, texte) {
    const messageContainer = document.getElementById('message-container');
    if (!messageContainer) return;

    const messageDiv = document.createElement('div');
    messageDiv.classList.add('alert', `alert-${type === 'error' ? 'danger' : 'success'}`);
    messageDiv.textContent = texte;
    messageContainer.appendChild(messageDiv);

    setTimeout(() => messageContainer.removeChild(messageDiv), 2000);
}

export function updateActionButtons(isMyTurn) {
    const prendreDeuxJetonsButton = document.getElementById("prendre-deux-jetons");
    const prendreTroisJetonsButton = document.getElementById("prendre-trois-jetons");

    if (prendreDeuxJetonsButton) prendreDeuxJetonsButton.disabled = !isMyTurn;
    if (prendreTroisJetonsButton) prendreTroisJetonsButton.disabled = !isMyTurn;
   
    document.querySelectorAll(".carte").forEach(carte => {
        carte.style.pointerEvents = isMyTurn ? 'auto' : 'none';
        carte.style.opacity = isMyTurn ? '1' : '0.5';
    });
}

export function updateBoardAndPlayerTokensMultiple(data) {
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

export function updateBoardAndPlayerTokensSingle(data) {
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

export function updateCurrentPlayer(data) {
    const joueurTourElement = document.getElementById("current_player");
    if (joueurTourElement) {
        joueurTourElement.innerText = "C'est au tour de : " + data.current_player;
    }
}


// Mise à jour des cartes affichées
export function updateCartesDisplay(cartes, gameInstance) {
    console.log("updateCartesDisplay appelé avec gameInstance :", gameInstance);
    
    const cartesContainer = document.querySelector('.cartes-plateau');
    cartesContainer.innerHTML = ''; // Effacer les cartes actuelles

    cartes.forEach(carte => {
        const carteDiv = document.createElement('div');
        carteDiv.classList.add('col-md-3', 'mb-4');
        carteDiv.innerHTML = `
            <div class="carte card h-100" data-id="${carte.id}">
                <img src="/static/${carte.image_path || carte.image}" class="card-img-top" alt="Image de la carte" style="width: 100px; height: 120px;">
                <div class="card-body">
                    <h5 class="card-title">Niveau ${carte.niveau}</h5>
                    <p class="card-text">
                        <strong>Bonus :</strong> ${carte.bonus.charAt(0).toUpperCase() + carte.bonus.slice(1)}<br>
                        <strong>Points de victoire :</strong> ${carte.points_victoire}
                    </p>
                    <p class="card-text"><strong>Coût :</strong></p>
                    <ul class="list-unstyled">
                        ${Object.entries(carte.cout).map(([couleur, quantite]) =>
                            `<li>${couleur.charAt(0).toUpperCase() + couleur.slice(1)} : ${quantite}</li>`
                        ).join('')}
                    </ul>
                </div>
                <div class="card-footer">
                    <button class="btn btn-warning reserver-carte-btn" data-id="${carte.id}">Réserver</button>
                </div>
            </div>
        `;
        cartesContainer.appendChild(carteDiv);
    });

    // Ré-attacher les écouteurs d'événements pour les nouvelles cartes et boutons "Réserver"
    cartesContainer.querySelectorAll(".carte").forEach(carte => {
        carte.addEventListener("click", gameInstance.handleCarteClick.bind(gameInstance));
    });
    cartesContainer.querySelectorAll(".reserver-carte-btn").forEach(button => {
        button.addEventListener("click", event => {
            event.stopPropagation();
            const carteId = button.getAttribute('data-id');
            gameInstance.reserverCarte(carteId);
        });
    });
}


export function updatePlayerPoints(joueur, points) {
    const pointsElement = document.querySelector(`#joueur-points-${joueur}`);
    if (pointsElement) {
        pointsElement.innerText = points;
    }
}



export function updateCartesAchetees(joueur, cartesAchetees) {
    // Sélectionnez le conteneur des cartes achetées du joueur
    const cartesAcheteesContainer = document.querySelector(`#joueur-cartes-achetees-${joueur}`);

    if (cartesAcheteesContainer) {
        // Effacer le contenu actuel
        cartesAcheteesContainer.innerHTML = '';

        if (cartesAchetees.length > 0) {
            cartesAchetees.forEach(carte => {
                const carteItem = document.createElement('li');
                carteItem.classList.add('m-2');
                carteItem.innerHTML = `
                    <img src="/static/${carte.image_path}" class="card-img-top" alt="Image de la carte" style="width: 100px; height: 120px;">
                    <p>${carte.niveau} - ${carte.bonus} - ${carte.points_victoire} points</p>
                `;
                cartesAcheteesContainer.appendChild(carteItem);
            });
        } else {
            cartesAcheteesContainer.innerHTML = '<p>Aucune carte achetée</p>';
        }
    }
}

export function updateCartesReservees(joueur, cartesReservees) {
    const cartesReserveesContainer = document.querySelector(`#joueur-cartes-reservees-${joueur}`);

    if (cartesReserveesContainer) {
        cartesReserveesContainer.innerHTML = '';

        if (cartesReservees.length > 0) {
            cartesReservees.forEach(carte => {
                const carteItem = document.createElement('li');
                carteItem.classList.add('m-2');
                carteItem.innerHTML = `
                    <img src="/static/${carte.image_path}" class="card-img-top carte-img" data-id="${carte.id}" alt="Image de la carte" style="width: 100px; height: 120px;">
                `;
                cartesReserveesContainer.appendChild(carteItem);
            });
        } else {
            cartesReserveesContainer.innerHTML = '<p>Aucune carte réservée</p>';
        }
    }
}






export function refreshPlayerTokens(joueur, jetons) {
    for (const [couleur, quantite] of Object.entries(jetons)) {
        const selector = `#joueur-jetons-${joueur}-${couleur} span`;
        const joueurJetonElement = document.querySelector(selector);
        if (joueurJetonElement) {
            joueurJetonElement.innerText = quantite;
        } else {
            console.error(`Élément non trouvé pour le sélecteur : ${selector}`);
        }
    }
}



export function updatePlayerTokens(joueur, jetons) {
    const colors = ['noir', 'bleu', 'blanc', 'rouge', 'vert', 'jaune']; // Liste complète des couleurs de jetons possibles
    const playerTokenContainer = document.querySelector(`#joueur-jetons-${joueur}`);

    if (playerTokenContainer) {
        playerTokenContainer.innerHTML = ''; // Efface le contenu actuel

        colors.forEach(couleur => {
            const quantite = jetons[couleur] || 0; // Si le jeton n'existe pas, on affiche 0
            const listItem = document.createElement('li');
            listItem.id = `joueur-jetons-${joueur}-${couleur}`;
            listItem.innerHTML = `${couleur.charAt(0).toUpperCase() + couleur.slice(1)} : <span>${quantite}</span>`;
            playerTokenContainer.appendChild(listItem);
        });
    }
}

export function updatePlateauJetons(plateauJetons) {
    for (const [couleur, quantite] of Object.entries(plateauJetons)) {
        const plateauJetonElement = document.querySelector(`#plateau-${couleur}-quantite span`);
        if (plateauJetonElement) {
            plateauJetonElement.innerText = quantite;
        }
    }
}

