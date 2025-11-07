# src/view/client/connexion_client_vue.py
from InquirerPy import inquirer
from view.reservations.mes_reservations_vue import MesReservationsVue
from view.vue_abstraite import VueAbstraite
from view.session import Session
from view.consulter.consulter_evenement_vue import ConsulterVue
from view.evenement.creer_evenement_vue import CreerEvenementVue
from view.evenement.modifier_evenement_vue import ModifierEvenementVue
from view.evenement.supprimer_evenement_vue import SupprimerEvenementVue
from view.consulter.liste_reservation_vue import ListeInscritsEvenementVue
# On importera la vue des réservations plus tard
# from view.reservations.mes_reservations_vue import MesReservationsVue


class ConnexionAdminVue(VueAbstraite):
    """
    Vue pour le menu d'un utilisateur admin
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
            "Consulter les événements",
            "Consulter mes réservations",
            "Consulter les inscriptions",
            "Créer un événement",
            "Mofidier un événement",
            "Supprimer un événement",
            "Retour (Se déconnecter)"
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
            
            case "Consulter les inscriptions":
                return ListeInscritsEvenementVue()
            
            case "Créer un événement":
                return CreerEvenementVue()
            
            case "Mofidier un événement":
                return ModifierEvenementVue

            case "Supprimer un événement":
                return SupprimerEvenementVue
            
            case "Retour (Se déconnecter)":
                Session().deconnexion()
                print("Déconnexion réussie.")
                return AccueilVue("Vous avez été déconnecté.")
