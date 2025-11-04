# view/auth/connexion_vue.py
from typing import Optional
from getpass import getpass

from view.accueil.accueil_vue import AccueilVue
# from dao.utilisateur_dao import UtilisateurDao  # à brancher si besoin
# from dao.participant_dao import ParticipantDao  # ou AdministrateurDao, selon le cas


class ConnexionVue:
    """
    Vue de connexion utilisateur.
    À brancher sur UtilisateurDao.authenticate(...) ou Participant/Administrateur DAO.
    """

    def afficher(self) -> None:
        print("\n--- CONNEXION ---")

    def choisir_menu(self) -> Optional[AccueilVue]:
        email = input("Email : ").strip()
        mot_de_passe = getpass("Mot de passe : ")

        # TODO: Brancher l'authentification réelle
        # user = UtilisateurDao().authenticate(email, mot_de_passe)
        # if user:
        #     print(f"Connecté : {user.prenom} {user.nom}")
        # else:
        #     print("Identifiants invalides")

        print("→ TODO: brancher l'authentification (UtilisateurDao/ParticipantDao/AdministrateurDao).")
        return AccueilVue("Vous êtes revenu au menu principal")
