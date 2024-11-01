import { updateCartesDisplay } from './ui.js';

document.addEventListener("DOMContentLoaded", function () {
    const resetButton = document.getElementById("reset-game");
    let isResetting = false;

    if (resetButton) {
        resetButton.addEventListener("click", function (event) {
            event.preventDefault();

            // Vérifier et afficher l'état actuel de isResetting pour débogage
            console.log("Reset button clicked, isResetting:", isResetting);
            
            if (isResetting) return;
            isResetting = true;
            resetButton.disabled = true;

            const resetUrl = resetButton.getAttribute("data-url");

            fetch(resetUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);

                    // Mise à jour du plateau de jetons
                    for (const [couleur, quantite] of Object.entries(data.plateau)) {
                        const plateauJetonElement = document.querySelector(`#plateau-${couleur}-quantite span`);
                        if (plateauJetonElement) {
                            plateauJetonElement.innerText = quantite;
                        }
                    }

                    // Mise à jour des jetons du joueur
                    for (const [joueur, jetons] of Object.entries(data.joueurs)) {
                        for (const [couleur, quantite] of Object.entries(jetons)) {
                            const joueurJetonElement = document.querySelector(`#joueur-jetons-${joueur}-${couleur} span`);
                            if (joueurJetonElement) {
                                joueurJetonElement.innerText = quantite;
                            }
                        }
                    }
                    // Mise à jour des bonus du joueur
                    if (data.bonus) {
                        for (const [joueur, bonus] of Object.entries(data.bonus)) {
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
                    }

                    // Mise à jour des cartes affichées
                    updateCartesDisplay(data.cartes, window.game); 
                } else {
                    alert("Erreur lors de la réinitialisation de la partie.");
                }
            })
            .catch(error => {
                console.error("Erreur :", error);
                alert("Erreur lors de la réinitialisation de la partie.");
            })
            .finally(() => {
                isResetting = false;
                resetButton.disabled = false;
                console.log("Final reset, isResetting:", isResetting); // Vérification finale
            });
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
