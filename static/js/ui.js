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


export function updateCartesDisplay(cartes, gameInstance) {
    console.log("updateCartesDisplay appelé avec gameInstance :", gameInstance);
    
    const cartesContainer = document.querySelector('.cartes-plateau');
    cartesContainer.innerHTML = ''; // Effacer les cartes actuelles

    cartes.forEach(carte => {
        const carteDiv = document.createElement('div');
        carteDiv.classList.add('col-md-3', 'mb-4');
        carteDiv.innerHTML = `
            <div class="carte card h-100" data-id="${carte.id}">
            
                <img src="/static/${carte.image_path}" class="card-img-top" alt="Image de la carte" style="width: 150px; height: 180px;">
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
            </div>
        `;
        cartesContainer.appendChild(carteDiv);
    });

    // Ré-attacher les écouteurs d'événements pour les nouvelles cartes
    cartesContainer.querySelectorAll(".carte").forEach(carte => {
        carte.addEventListener("click", gameInstance.handleCarteClick.bind(gameInstance));
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
                    <img src="/static/${carte.image_path}" class="card-img-top" alt="Image de la carte" style="width: 150px; height: 180px;">
                    <p>${carte.niveau} - ${carte.bonus} - ${carte.points_victoire} points</p>
                `;
                cartesAcheteesContainer.appendChild(carteItem);
            });
        } else {
            cartesAcheteesContainer.innerHTML = '<p>Aucune carte achetée</p>';
        }
    }
}

