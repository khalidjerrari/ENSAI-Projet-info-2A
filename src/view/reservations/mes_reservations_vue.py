# src/view/reservations/mes_reservations_vue.py
from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session

# On passe par les services
from service.reservation_service import ReservationService
from service.evenement_service import EvenementService


class MesReservationsVue(VueAbstraite):
    """
    Vue pour afficher les réservations d'un utilisateur.

    Adaptée au nouveau schéma + couche service :
       - Plus d'accès direct aux DAO.
       - Passe par ReservationService et EvenementService.
       - Supprime toute référence à fk_transport.
    """

    def __init__(self, message: str = ""):
        super().__init__(message)
        self.session = Session()
        self.user = self.session.utilisateur
        self.reservation_service = ReservationService()
        self.evenement_service = EvenementService()

    def afficher(self):
        """
        Affiche la liste des réservations de l’utilisateur connecté.
        """
        super().afficher()

        if not self.session.est_connecte() or not self.user:
            print("Vous n'êtes pas connecté.")
            return

        print(f"--- Vos Réservations ({self.user.prenom}) ---")

        try:
            # On passe par le service
            reservations = self.reservation_service.get_reservations_by_user(self.user.id_utilisateur)

            if not reservations:
                print("\nVous n'avez aucune réservation pour le moment.")
                return

            print("\nVoici la liste de vos réservations :")
            for res in reservations:
                evt = None
                try:
                    if getattr(res, "fk_evenement", None):
                        evt = self.evenement_service.get_evenement_by_id(res.fk_evenement)
                except Exception:
                    evt = None  # On ne bloque pas l’affichage si l’événement n’est pas accessible

                print(f"\n[Réservation #{res.id_reservation}]")
                if evt:
                    print(f"  Événement : {evt.titre} — le {getattr(evt, 'date_evenement', '')}")
                    ville = getattr(evt, "ville", None)
                    adresse = getattr(evt, "adresse", None)
                    if ville or adresse:
                        print(f"  Lieu      : {adresse or '—'}{(' | ' + ville) if ville else ''}")
                else:
                    print(f"  Événement : #{getattr(res, 'fk_evenement', '—')} (détails indisponibles)")

                dr = getattr(res, "date_reservation", None)
                if dr:
                    try:
                        print(f"  Réservé le: {dr.strftime('%d/%m/%Y à %H:%M')}")
                    except Exception:
                        print(f"  Réservé le: {dr}")

                print(
                    "  Trajet    : Aller? {} | Retour? {}".format(
                        "Oui" if getattr(res, "bus_aller", False) else "Non",
                        "Oui" if getattr(res, "bus_retour", False) else "Non",
                    )
                )

                print(
                    "  Options   : Adhérent? {} | SAM? {} | Boisson? {}".format(
                        "Oui" if getattr(res, "adherent", False) else "Non",
                        "Oui" if getattr(res, "sam", False) else "Non",
                        "Oui" if getattr(res, "boisson", False) else "Non",
                    )
                )

        except Exception as e:
            print(f"\n Erreur lors de la récupération de vos réservations : {e}")

    def choisir_menu(self):
        """
        Gère le retour au menu client après consultation des réservations.
        """
        from view.client.connexion_client_vue import ConnexionClientVue

        if not self.session.est_connecte() or not self.user:
            return ConnexionClientVue()

        inquirer.select(
            message="Que souhaitez-vous faire ?",
            choices=["Retour au menu client"],
        ).execute()

        return ConnexionClientVue()
