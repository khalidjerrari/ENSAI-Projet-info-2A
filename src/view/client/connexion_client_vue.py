# src/view/client/connexion_client_vue.py
from InquirerPy import inquirer
from view.reservations.mes_reservations_vue import MesReservationsVue
from view.vue_abstraite import VueAbstraite
from view.session import Session
from view.consulter.consulter_evenement_vue import ConsulterVue
from view.auth.suppression_compte_vue import SuppressionCompteVue
from view.auth.modification_compte_vue import ModificationCompteVue


class ConnexionClientVue(VueAbstraite):
    """
    Vue pour le menu d'un utilisateur non-admin (client).
    """
    def __init__(self, message: str = ""):
        super().__init__(message)
        # Ne pas stocker l'utilisateur ici (risque d'être obsolète)
        # self.user = Session().utilisateur

    def afficher(self):
        super().afficher()

    def choisir_menu(self):
        from view.accueil.accueil_vue import AccueilVue

        # Relecture live de la session
        user = Session().utilisateur
        if not user:
            print("Erreur : Vous n'êtes plus connecté.")
            return AccueilVue()

        message = f"Connecté en tant que : {user.prenom} {user.nom}"
        choices = [
            "Consulter les événements",
            "Consulter mes réservations",
            "Supprimer mon compte",
            "Modifier mon compte",
            "Retour (Se déconnecter)"
        ]

        choix = inquirer.select(
            message=message,
            choices=choices,
        ).execute()

        match choix:
            case "Consulter les événements":
                return ConsulterVue()

            case "Consulter mes réservations":
                return MesReservationsVue()

            case "Supprimer mon compte":
                return SuppressionCompteVue()

            case "Modifier mon compte":
                return ModificationCompteVue()

            case "Retour (Se déconnecter)":
                Session().deconnexion()   # si tu passes à une Session de classe, remplace par: Session.deconnexion()
                print("Déconnexion réussie.")
                return AccueilVue("Vous avez été déconnecté.")
