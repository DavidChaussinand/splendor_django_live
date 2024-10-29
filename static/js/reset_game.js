// reset_game.js

document.addEventListener("DOMContentLoaded", function () {
    const resetButton = document.getElementById("reset-game");
    let isResetting = false;

    if (resetButton) {
        resetButton.addEventListener("click", function (event) {
            console.log("Reset button clicked");
            console.trace();
            event.preventDefault();
            
            if (isResetting) return;
            isResetting = true;
            resetButton.disabled = true;

            // Récupère l'URL depuis l'attribut `data-url`
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

                    // Mise à jour du plateau
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
                } else {
                    alert("Erreur lors de la réinitialisation de la partie.");
                }
            })
            .catch(error => console.error("Erreur :", error))
            .finally(() => {
                isResetting = false;
                resetButton.disabled = false;
            });
        });
    }

    // Fonction pour obtenir le token CSRF pour les requêtes POST
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
