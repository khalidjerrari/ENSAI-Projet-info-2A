# view/auth/connexion_vue.py
from __future__ import annotations
from typing import Optional
from getpass import getpass
import logging

from view.accueil.accueil_vue import AccueilVue
from view.session import Session
from dao.UtilisateurDAO import UtilisateurDao

logger = logging.getLogger(__name__)


class ConnexionVue:
    """
    Vue de connexion utilisateur.
    Utilise UtilisateurDao.authenticate(email, mot_de_passe).
    """

    def __init__(self, titre: str = "Connexion à l'application") -> None:
        self.titre = titre
        self.dao = UtilisateurDao()

    def afficher(self) -> None:
        print("\n" + "-" * 50)
        print(self.titre.center(50))
        print("-" * 50)

    def choisir_menu(self) -> Optional[AccueilVue]:
        # --- Saisie ---
        email = input("Email : ").strip()
        mot_de_passe = input("Mot de passe : ")

        if not email or not mot_de_passe:
            print("Email et mot de passe sont obligatoires.")
            return AccueilVue("Retour au menu principal")

        # --- Authentification ---
        try:
            user = self.dao.authenticate(email=email, mot_de_passe=mot_de_passe)
        except Exception as e:
            logger.exception("Erreur d'authentification: %s", e)
            print("Erreur technique pendant l’authentification.")
            return AccueilVue("Retour au menu principal")

        if not user:
            print("Identifiants invalides.")
            return AccueilVue("Retour au menu principal")

        # --- Mise en session + feedback ---
        Session().connexion(user)
        role = "Administrateur" if getattr(user, "administrateur", False) else "Participant"
        print(f"Connecté : {user.prenom} {user.nom} — {role}")

        return AccueilVue(f"Bienvenue {user.prenom} !")
