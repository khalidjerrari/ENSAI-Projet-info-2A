# src/view/reservations/mes_reservations_vue.py
from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session
from dao.ReservationDAO import ReservationDao

class MesReservationsVue(VueAbstraite):
    """
    Vue pour afficher les réservations d'un utilisateur.
    """
    def __init__(self, message=""):
        super().__init__(message)
        self.user = Session().utilisateur
        self.dao = ReservationDao()

    def afficher(self):
        super().afficher()
        
        if not self.user:
            print("Erreur : Vous n'êtes pas connecté.")
            return

        print(f"--- 🗓️ Vos Réservations ({self.user.prenom}) ---")
        
        try:
            reservations = self.dao.find_by_user(self.user.id_utilisateur)
            
            if not reservations:
                print("\nVous n'avez aucune réservation pour le moment.")
                return

            print("\nVoici la liste de vos réservations :")
            for res in reservations:
                # res est un objet ReservationModelOut
                print(f"\n[Réservation #{res.id_reservation}]")
                print(f"  Transport ID: {res.fk_transport}")
                print(f"  Date: {res.date_reservation.strftime('%d/%m/%Y à %H:%M')}")
                print(f"  Options: Adhérent? {'Oui' if res.adherent else 'Non'}, "
                      f"SAM? {'Oui' if res.sam else 'Non'}, "
                      f"Boisson? {'Oui' if res.boisson else 'Non'}")
        
        except Exception as e:
            print(f"\n❌ Erreur lors de la récupération de vos réservations : {e}")


    def choisir_menu(self):
        # On importe ici pour éviter la boucle circulaire
        from view.client.connexion_client_vue import ConnexionClientVue

        if not self.user:
            return ConnexionClientVue() # Retour au menu client

        # Menu simple pour juste revenir en arrière
        choix = inquirer.select(
            message="Que souhaitez-vous faire ?",
            choices=["Retour au menu client"],
        ).execute()

        # Quoi qu'il arrive, on retourne au menu client
        return ConnexionClientVue()