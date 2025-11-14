# view/auth/connexion_vue.py
from __future__ import annotations
from typing import Optional
import logging
import pwinput

from view.session import Session
from service.utilisateur_service import UtilisateurService  # Nouveau : on passe par le service

logger = logging.getLogger(__name__)


class ConnexionVue:
    """
    Vue de connexion utilisateur.
    Utilise UtilisateurService.authenticate_user(email, mot_de_passe).
    """

    def __init__(self, titre: str = "Connexion à l'application") -> None:
        self.titre = titre
        self.service = UtilisateurService()  # Remplace le DAO par le Service

    def afficher(self) -> None:
        print("\n" + "-" * 50)
        print(self.titre.center(50))
        print("-" * 50)

    def choisir_menu(self) -> Optional["AccueilVue"]:
        from view.accueil.accueil_vue import AccueilVue

        # --- Saisie utilisateur ---
        email = input("Email : ").strip()
        mot_de_passe = pwinput.pwinput(prompt="Mot de passe : ", mask="*")

        if not email or not mot_de_passe:
            print(" Email et mot de passe sont obligatoires.")
            return AccueilVue("Retour au menu principal")

        # --- Authentification via le service ---
        try:
            user = self.service.authenticate_user(email=email, password=mot_de_passe)
        except ValueError as e:
            # Cas d’erreur métier (identifiants incorrects, utilisateur non trouvé, etc.)
            print(f" {e}")
            return AccueilVue("Retour au menu principal")
        except Exception as e:
            # Cas d’erreur technique (connexion DB, etc.)
            logger.exception("Erreur d'authentification: %s", e)
            print("Erreur technique pendant l’authentification.")
            return AccueilVue("Retour au menu principal")

        # --- Si succès : mise en session + feedback ---
        Session().connexion(user)
        role = "Administrateur" if getattr(user, "administrateur", False) else "Participant"
        print(f"Connecté : {user.prenom} {user.nom} — {role}")

        return AccueilVue(f"Bienvenue {user.prenom} !")
