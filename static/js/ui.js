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

export function updateCartesDisplay(cartes, pilesCounts, gameInstance) {
    console.log("updateCartesDisplay appelé avec cartes :", cartes);
    console.log("updateCartesDisplay appelé avec pilesCounts :", pilesCounts);
    
    // Sélectionnez les conteneurs pour chaque niveau de carte
    const cartesPlateauContainers = document.querySelectorAll('.cartes-plateau');

    // Vérifier que nous avons bien trois conteneurs
    if (cartesPlateauContainers.length !== 3) {
        console.error("Le nombre de conteneurs 'cartes-plateau' ne correspond pas aux niveaux attendus.");
        return;
    }

    [1, 2, 3].forEach((niveau, index) => {
        const cartesContainer = cartesPlateauContainers[index];
        if (!cartesContainer) return;

        cartesContainer.innerHTML = ''; // Efface le contenu actuel

        // Ajouter la pile de cartes
        const pileDiv = document.createElement('div');
        pileDiv.classList.add('col-md-2', 'mb-4');

        let imagePileSrc = '';
        let cartesPileRestantes = 0;

        // Déterminer l'image de la pile et le nombre de cartes restantes
        if (niveau === 1) {
            imagePileSrc = '/static/images/cartes/fond_de_carte_rouge.jpg';
            cartesPileRestantes = pilesCounts.niveau_1; // Nombre de cartes restantes pour le niveau 1
        } else if (niveau === 2) {
            imagePileSrc = '/static/images/cartes/fond_de_carte_jaune.jpg';
            cartesPileRestantes = pilesCounts.niveau_2; // Nombre de cartes restantes pour le niveau 2
        } else if (niveau === 3) {
            imagePileSrc = '/static/images/cartes/fond_de_carte_orange.jpg';
            cartesPileRestantes = pilesCounts.niveau_3; // Nombre de cartes restantes pour le niveau 3
        }

        // Générer le HTML pour la pile de cartes
        pileDiv.innerHTML = `
            <div class="pile-de-carte">
                <img src="${imagePileSrc}" class="card-img-pile pile-carte" data-niveau="${niveau}" alt="Pile de cartes">
                <p>Il reste ${cartesPileRestantes} carte(s)</p>
            </div>
        `;
        cartesContainer.appendChild(pileDiv);

        // Filtrer les cartes visibles pour ce niveau
        const cartesNiveau = cartes.filter(carte => carte.niveau === niveau);

        // Ajouter les cartes visibles
        cartesNiveau.forEach(carte => {
            const carteDiv = document.createElement('div');
            carteDiv.classList.add('col-md-2', 'mb-4');
            carteDiv.innerHTML = `
                <div class="carte card h-100" data-id="${carte.id}">
                    <img src="/static/${carte.image_path}" class="card-img-top" alt="Image de la carte">
                    <div class="card-footer">
                        <button class="btn btn-warning reserver-carte-btn" data-id="${carte.id}">Réserver</button>
                    </div>
                </div>
            `;
            cartesContainer.appendChild(carteDiv);
        });

        // Réattacher les gestionnaires d'événements pour les nouvelles cartes
        cartesContainer.querySelectorAll(".carte").forEach(carte => {
            carte.addEventListener("click", gameInstance.handleCarteClick.bind(gameInstance));
        });

        // Réattacher les gestionnaires d'événements pour les boutons "Réserver"
        cartesContainer.querySelectorAll(".reserver-carte-btn").forEach(button => {
            button.addEventListener("click", event => {
                event.stopPropagation();
                const carteId = button.getAttribute("data-id");
                gameInstance.reserverCarte(carteId);
            });
        });

        // Réattacher l'événement pour la pile de cartes
        pileDiv.querySelector(".pile-carte").addEventListener("click", (event) => {
            const niveauPile = event.currentTarget.getAttribute("data-niveau");
            gameInstance.reserverCarteFromPile(niveauPile);
        });
    });
}







export function updatePlayerPoints(joueur, points) {
    const pointsElement = document.querySelector(`#joueur-points-${joueur}`);
    if (pointsElement) {
        pointsElement.innerText = points; // Met à jour le total des points affiché
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
        cartesReserveesContainer.innerHTML = ''; // Vider le contenu actuel

        if (cartesReservees.length > 0) {
            // Vérifier si le joueur est le joueur actuel
            if (joueur === monNomUtilisateur) {
                // Afficher les images des cartes réservées pour le joueur actuel
                cartesReservees.forEach(carte => {
                    const imgElement = document.createElement('img');
                    imgElement.src = `/static/${carte.image_path}`;
                    imgElement.alt = `Carte réservée`;
                    imgElement.classList.add('img-carte-reservées');
                    imgElement.dataset.id = carte.id;
                    cartesReserveesContainer.appendChild(imgElement);
                });
            } else {
                // Pour les adversaires, afficher une image en fonction du niveau de la carte
                cartesReservees.forEach((carte, index) => {
                    const pElement = document.createElement('p');
            
                    // Appliquer les classes selon la position de la carte dans la liste
                    if (index === 0) {
                        pElement.classList.add('start');
                    } else if (index === 1) {
                        pElement.classList.add('center');
                    } else if (index === 2) {
                        pElement.classList.add('end');
                    }
            
                    // Créer l'élément image
                    const imgElement = document.createElement('img');
                    imgElement.classList.add('card-img-pile-reserve');
            
                    // Définir le src de l'image en fonction du niveau de la carte
                    if (carte.niveau === 1) {
                        imgElement.src = '/static/images/cartes/fond_de_carte_rouge.jpg';
                    } else if (carte.niveau === 2) {
                        imgElement.src = '/static/images/cartes/fond_de_carte_jaune.jpg';
                    } else if (carte.niveau === 3) {
                        imgElement.src = '/static/images/cartes/fond_de_carte_orange.jpg';
                    }
            
                    // Ajouter l'image à l'élément p
                    pElement.appendChild(imgElement);
            
                    // Ajouter l'élément p au conteneur
                    cartesReserveesContainer.appendChild(pElement);
                });
            }
        } else {
            cartesReserveesContainer.innerHTML = '<p>Aucune carte réservée</p>';
        }
    } else {
        console.error(`Conteneur des cartes réservées non trouvé pour le joueur : ${joueur}`);
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
    const colors = ['noir', 'bleu', 'blanc', 'rouge', 'vert', 'jaune'];
    const playerTokenContainer = document.querySelector(`#joueur-jetons-${joueur}`);

    if (playerTokenContainer) {
        playerTokenContainer.innerHTML = ''; // Efface le contenu actuel

        colors.forEach(couleur => {
            const quantite = jetons[couleur] || 0;

            // Crée un bouton avec les mêmes classes et structure que dans le HTML
            const button = document.createElement('button');
            button.classList.add('btn-custom', `btn-${couleur}`, 'btn-small');
            button.id = `joueur-jetons-${joueur}-${couleur}`;
            button.type = 'button';
            

            const span = document.createElement('span');
            span.innerText = quantite;
            button.appendChild(span);

            playerTokenContainer.appendChild(button);
        });
    } else {
        console.error(`Conteneur de jetons non trouvé pour le joueur : ${joueur}`);
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



export function updatePlayerBonus(joueur, bonus) {
    const bonusList = document.querySelector(`#joueur-bonus-list-${joueur}`);

    if (bonusList) {
        bonusList.innerHTML = ''; // Efface le contenu actuel

        for (const [couleur, quantite] of Object.entries(bonus)) {
            const button = document.createElement('button');
            button.classList.add('btn-custom', `btn-${couleur}_bonus`, 'btn-small_bonus');
            button.id = `joueur-bonus-${joueur}-${couleur}`;
            button.type = 'button';

            // Ajoute une classe supplémentaire si c'est un adversaire
            if (joueur !== monNomUtilisateur) {
                button.classList.add('btn-small_bonus-adversaire');
            }

            const span = document.createElement('span');
            span.innerText = quantite;
            button.appendChild(span);

            bonusList.appendChild(button);
        }
    } else {
        console.error(`Liste des bonus non trouvée pour le joueur : ${joueur}`);
    }
}


// ui.js

export function updateNoblesAcquis(noblesAcquis, joueur) {
    if (!noblesAcquis || !Array.isArray(noblesAcquis)) {
        console.error('noblesAcquis est undefined ou n\'est pas une liste');
        return;
    }

    // Sélectionnez le conteneur spécifique au joueur actuel
    const acquiredNoblesContainer = document.querySelector(`#acquired-nobles-section[data-username="${joueur}"] #acquired-nobles-list`);
    if (!acquiredNoblesContainer) {
        console.error(`Conteneur des nobles acquis non trouvé pour le joueur ${joueur}`);
        return;
    }

    acquiredNoblesContainer.innerHTML = ''; // Vider le contenu actuel

    if (noblesAcquis.length === 0) {
        acquiredNoblesContainer.innerHTML = '<p>Aucun noble acquis pour le moment</p>';
        return;
    }

    noblesAcquis.forEach(noble => {
        const li = document.createElement('li');
        li.innerHTML = `<img src="/static/${noble.image_path}" class="noble-image" alt="Image du noble">`;
        acquiredNoblesContainer.appendChild(li);
    });
}


