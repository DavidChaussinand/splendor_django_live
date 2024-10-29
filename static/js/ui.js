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
