from InquirerPy import inquirer

from utils.reset_database import ResetDatabase

from view.vue_abstraite import VueAbstraite
from view.session import Session


class AccueilVue(VueAbstraite):
    """Vue d'accueil de l'application"""

    def choisir_menu(self):
        """Choix du menu suivant

        Return
        ------
        view
            Retourne la vue choisie par l'utilisateur dans le terminal
        """

        print("\n" + "-" * 50 + "\nAccueil\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Créer un compte",
                "Se connecter",
                "Consulter les événements",
                "Créer les événements",
                "Quitter",
            ],
        ).execute()

        match choix:
            case "Quitter":
                pass

            case "Se connecter":
                from view.auth.connexion_vue import ConnexionVue
                return ConnexionVue("Connexion à l'application")

            case "Créer un compte":
                from view.auth.creation_compte_vue import CreationCompteVue
                return CreationCompteVue("Création de compte joueur")

            case "Consulter les événements":  # Je sais pas comment on fait ça
                from view.consulter.consulter_evenement_vue import ConsulterVue
                return ConsulterVue()

            case "Créer les événements":
                from view.evenement.creer_evenement_vue import CreerEvenementVue
                return CreerEvenementVue()

            case "Ré-initialiser la base de données":  # On garde ça ??
                succes = ResetDatabase().lancer()
                message = (
                    f"Ré-initilisation de la base de données - {'SUCCES' if succes else 'ECHEC'}"
                )
                return AccueilVue(message)
