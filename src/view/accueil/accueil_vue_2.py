# view/accueil/accueil_vue.py
from typing import Optional

from view.consulter.consulter_vue import ConsulterVue
from view.auth.connexion_vue import ConnexionVue
from view.auth.creation_compte_vue import CreationCompteVue


class AccueilVue:
    """
    Vue d'accueil / menu principal.
    API attendue par le main :
      - afficher()
      - choisir_menu() -> retourne la prochaine vue (ou None pour quitter)
    """

    def __init__(self, titre: str = "Bienvenue"):
        self.titre = titre

    def afficher(self) -> None:
        print("\n" + "=" * 40)
        print(f" {self.titre}")
        print("=" * 40)
        print("0 - Menu principal")
        print("1 - Consulter")
        print("2 - Se connecter")
        print("3 - Créer un compte")
        print("4 - Quitter")
        print("-" * 40)

    def choisir_menu(self) -> Optional["AccueilVue"]:
        while True:
            choix = input(" Entrez votre choix (0-4) : ").strip()
            if choix not in {"0", "1", "2", "3", "4"}:
                print(" Choix invalide. Merci d’entrer un nombre entre 0 et 4.")
                continue

            if choix == "0":
                # Rester sur le menu principal
                return AccueilVue("Menu principal")
            if choix == "1":
                return ConsulterVue()
            if choix == "2":
                return ConnexionVue()
            if choix == "3":
                return CreationCompteVue()
            if choix == "4":
                # Signale au main de sortir de la boucle
                return None
