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

                    // Mise à jour des cartes affichées
                    updateCartesDisplay(data.cartes);  
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
