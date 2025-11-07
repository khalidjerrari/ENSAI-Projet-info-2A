# Dans src/view/accueil/accueil_vue.py

# ... (tous tes imports en haut) ...
# AJOUTE L'IMPORT DE LA NOUVELLE VUE :
from view.client.connexion_client_vue import ConnexionClientVue

# --- Imports en haut du fichier ---
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from view.session import Session 
from view.auth.connexion_vue import ConnexionVue
from view.auth.creation_compte_vue import CreationCompteVue
from view.consulter.consulter_evenement_vue import ConsulterVue
# On importera la vue admin plus tard
# from view.admin.connexion_admin_vue import ConnexionAdminVue

class AccueilVue(VueAbstraite):
    
    # ... (__init__ et afficher ne changent PAS) ...
    # Laisse-les comme ils sont. C'est choisir_menu qui change.

    def choisir_menu(self):
        """
        Choix du menu suivant.
        Devient un AIGUILLEUR si l'utilisateur est connecté.
        """
        self.user = Session().utilisateur # On met à jour self.user

        # --- PARTIE 1 : AIGUILLAGE ---
        if self.user:
            # L'utilisateur EST connecté
            if self.user.administrateur:
                from view.administrateur.connexion_admin_vue import ConnexionAdminVue
                # C'est un ADMIN
                # return ConnexionAdminVue()
                return ConnexionAdminVue(f"Bienvenue {self.user.prenom} !")
                
            else:
                # C'est un CLIENT (non-admin)
                # On le redirige direct vers le menu client 2.1
                return ConnexionClientVue(f"Bienvenue {self.user.prenom} !")

        # --- PARTIE 2 : MENU NON-CONNECTÉ ---
        # Si on arrive ici, c'est que self.user était None.
        
        message = "Faites votre choix :"
        choices_list = [
            "Consulter les événements",
            "Se connecter",
            "Créer un compte",
            "Quitter",
        ]

        print("\n" + "-" * 10 + "\n🚌 Shotgun ENSAI\n" + "-" * 10 + "\n")
        choix = inquirer.select(
            message=message,
            choices=choices_list,
        ).execute()

        # Gestion du choix non-connecté
        match choix:
            case "Quitter":
                return None
            case "Consulter les événements":
                return ConsulterVue()
            case "Se connecter":
                from view.auth.connexion_vue import ConnexionVue
                return ConnexionVue("Connexion à l'application")
            case "Créer un compte":
                from view.auth.creation_compte_vue import CreationCompteVue
                return CreationCompteVue("Création de compte")