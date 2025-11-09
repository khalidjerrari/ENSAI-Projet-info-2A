# src/view/client/connexion_client_vue.py
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from view.session import Session

# Import des vues accessibles depuis le menu admin
from view.consulter.consulter_evenement_vue import ConsulterVue
from view.reservations.mes_reservations_vue import MesReservationsVue
from view.consulter.liste_reservation_vue import ListeInscritsEvenementVue
from view.consulter.statistiques_vue import StatistiquesInscriptionsVue
from view.evenement.creer_evenement_vue import CreerEvenementVue
from view.evenement.modifier_evenement_vue import ModifierEvenementVue
from view.evenement.supprimer_evenement_vue import SupprimerEvenementVue

# ✅ On importe le service utilisateur pour la gestion de session
from service.utilisateur_service import UtilisateurService


class ConnexionAdminVue(VueAbstraite):
    """
    Vue pour le menu d’un utilisateur administrateur.
    Gère les actions possibles via le UtilisateurService (connexion/déconnexion).
    """

    def __init__(self, message: str = ""):
        super().__init__(message)
        self.utilisateur_service = UtilisateurService()
        self.session = Session()
        self.user = self.session.utilisateur

    def afficher(self):
        super().afficher()
        print("\n--- Menu Administrateur ---")

    def choisir_menu(self):
        from view.accueil.accueil_vue import AccueilVue

        # Vérification de la session
        user = self.session.utilisateur
        if not user:
            print("⚠️  Vous n'êtes plus connecté.")
            return AccueilVue("Session expirée, veuillez vous reconnecter.")

        # Message d’accueil
        message = f"Connecté en tant que : {user.prenom} {user.nom} (Admin)"
        choices = [
            "Consulter les événements",
            "Consulter mes réservations",
            "Consulter les inscriptions",
            "Créer un événement",
            "Modifier un événement",
            "Supprimer un événement",
            "Statistiques des inscriptions",
            "Retour (Se déconnecter)"
        ]

        choix = inquirer.select(
            message=message,
            choices=choices,
        ).execute()

        # Gestion des redirections
        match choix:
            case "Consulter les événements":
                return ConsulterVue()

            case "Consulter mes réservations":
                return MesReservationsVue()

            case "Consulter les inscriptions":
                return ListeInscritsEvenementVue()

            case "Créer un événement":
                return CreerEvenementVue()

            case "Modifier un événement":
                return ModifierEvenementVue()

            case "Supprimer un événement":
                return SupprimerEvenementVue()

            case "Statistiques des inscriptions":
                return StatistiquesInscriptionsVue()

            case "Retour (Se déconnecter)":
                try:
                    self.utilisateur_service.deconnexion()  # Passe par le service
                    print(" Déconnexion réussie.")
                except Exception as e:
                    print(f"Erreur lors de la déconnexion : {e}")
                return AccueilVue("Vous avez été déconnecté.")
