# src/view/client/connexion_client_vue.py
from InquirerPy import inquirer
from view.reservations.mes_reservations_vue import MesReservationsVue
from view.vue_abstraite import VueAbstraite
from view.session import Session
from view.consulter.consulter_evenement_vue import ConsulterVue
from view.auth.suppression_compte_vue import SuppressionCompteVue
from view.auth.modification_compte_vue import ModificationCompteVue
# On importera la vue des réservations plus tard
# from view.reservations.mes_reservations_vue import MesReservationsVue


class ConnexionClientVue(VueAbstraite):
    """
    Vue pour le menu d'un utilisateur non-admin (client).
    """
    def __init__(self, message=""):
        super().__init__(message)
        self.user = Session().utilisateur # Récupère l'utilisateur connecté

    def afficher(self):
        super().afficher()

    def choisir_menu(self):
        from view.accueil.accueil_vue import AccueilVue
        
        if not self.user:
            # Sécurité : si l'utilisateur s'est déconnecté, on le renvoie
            print("Erreur : Vous n'êtes plus connecté.")
            return AccueilVue()

        # Construction du message d'accueil et des choix
        message = f"Connecté en tant que : {self.user.prenom} {self.user.nom}"
        choices = [
            "Consulter les événements", # 2.1.1
            "Consulter mes réservations", # 2.1.2
            "Supprimer mon compte",
            "Modifier mon compte",
            "Retour (Se déconnecter)" # 2.1.3 (Quitter)
        ]

        # Affichage du menu InquirerPy
        choix = inquirer.select(
            message=message,
            choices=choices,
        ).execute()

        # Gestion du choix
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
                Session().deconnexion()
                print("Déconnexion réussie.")
                return AccueilVue("Vous avez été déconnecté.")