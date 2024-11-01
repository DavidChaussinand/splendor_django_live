// main.js

import { Game } from './gameLogic.js';

document.addEventListener("DOMContentLoaded", function () {
    // Ces variables doivent être définies dans votre template Django
    // Assurez-vous qu'elles sont accessibles en JavaScript


    // Initialiser le jeu
    window.game = new Game(nom_partie, monNomUtilisateur, currentPlayer);
});
