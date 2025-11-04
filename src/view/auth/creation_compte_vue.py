# view/auth/creation_compte_vue.py
from typing import Optional
from getpass import getpass

from view.accueil.accueil_vue import AccueilVue
# from dao.utilisateur_dao import UtilisateurDao
# from models.utilisateur_models import UtilisateurModelIn


class CreationCompteVue:
    """
    Vue de création de compte.
    À brancher sur UtilisateurDao.create(UtilisateurModelIn(...))
    """

    def afficher(self) -> None:
        print("\n--- CRÉER UN COMPTE ---")

    def choisir_menu(self) -> Optional[AccueilVue]:
        nom = input("Nom : ").strip()
        prenom = input("Prénom : ").strip()
        telephone = input("Téléphone (optionnel) : ").strip() or None
        email = input("Email : ").strip()
        mot_de_passe = getpass("Mot de passe : ")
        mot_de_passe2 = getpass("Confirmez le mot de passe : ")

        if mot_de_passe != mot_de_passe2:
            print("❌ Les mots de passe ne correspondent pas.")
            return AccueilVue("Création annulée — retour au menu principal")

        # TODO: appel réel à la couche DAO
        # user_in = UtilisateurModelIn(
        #     nom=nom, prenom=prenom, telephone=telephone,
        #     email=email, mot_de_passe=mot_de_passe, administrateur=False
        # )
        # user_out = UtilisateurDao().create(user_in)
        # print(f"Compte créé : {user_out.prenom} {user_out.nom} (id={user_out.id_utilisateur})")

        print("→ TODO: brancher la création de compte (UtilisateurDao.create).")
        return AccueilVue("Compte créé (simulation) — retour au menu principal")
