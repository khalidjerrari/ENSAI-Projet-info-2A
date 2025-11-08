# src/view/accueil/accueil_vue.py

from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from view.session import Session 
from view.auth.connexion_vue import ConnexionVue
from view.auth.creation_compte_vue import CreationCompteVue
from view.consulter.consulter_evenement_vue import ConsulterVue
from view.client.connexion_client_vue import ConnexionClientVue

# On garde l'import admin différé pour éviter les cycles
# importé uniquement au moment du besoin
# from view.administrateur.connexion_admin_vue import ConnexionAdminVue


class AccueilVue(VueAbstraite):
    """
    Vue d’accueil de l’application.
    Sert d’aiguillage entre :
      - Connexion / Création de compte / Consultation
      - Espace administrateur ou client selon le profil.
    """

    def choisir_menu(self):
        """
        Choix du menu suivant.
        Devient un aiguillage si l'utilisateur est connecté.
        """
        self.user = Session().utilisateur  # Récupère l’utilisateur connecté (si existant)

        # --- PARTIE 1 : UTILISATEUR CONNECTÉ ---
        if self.user:
            # Mise à jour : self.user vient désormais d’un service (après authentification)
            if getattr(self.user, "administrateur", False):
                # --- Vue administrateur ---
                from view.administrateur.connexion_admin_vue import ConnexionAdminVue
                return ConnexionAdminVue(f"Bienvenue {self.user.prenom} !")
            else:
                # --- Vue client ---
                return ConnexionClientVue(f"Bienvenue {self.user.prenom} !")

        # --- PARTIE 2 : UTILISATEUR NON CONNECTÉ ---
        message = "Faites votre choix :"
        choices_list = [
            "Consulter les événements",
            "Se connecter",
            "Créer un compte",
            "Quitter",
        ]

        print("\n" + "-" * 10 + "\n🚌 Shotgun ENSAI\n" + "-" * 10 + "\n")
        choix = inquirer.select(message=message, choices=choices_list).execute()

        match choix:
            case "Quitter":
                return None
            case "Consulter les événements":
                return ConsulterVue()
            case "Se connecter":
                return ConnexionVue("Connexion à l'application")
            case "Créer un compte":
                return CreationCompteVue("Création de compte")
