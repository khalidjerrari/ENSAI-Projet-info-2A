# src/view/reservations/mes_reservations_vue.py
from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session
from dao.ReservationDAO import ReservationDao
from dao.EvenementDAO import EvenementDao


class MesReservationsVue(VueAbstraite):
    """
    Vue pour afficher les réservations d'un utilisateur.

    ✅ Adaptée au nouveau schéma SQL :
       - Suppression de l'affichage `fk_transport` (n'existe plus).
       - Affichage des informations d'événement via `fk_evenement`.
       - Affichage des choix bus (aller/retour) et options (adhérent, sam, boisson).
    """

    def __init__(self, message: str = ""):
        super().__init__(message)
        self.session = Session()
        self.user = self.session.utilisateur
        self.reservation_dao = ReservationDao()
        self.evenement_dao = EvenementDao()

    def afficher(self):
        super().afficher()

        if not self.session.est_connecte() or not self.user:
            print("Erreur : Vous n'êtes pas connecté.")
            return

        print(f"--- 🗓️ Vos Réservations ({self.user.prenom}) ---")

        try:
            reservations = self.reservation_dao.find_by_user(self.user.id_utilisateur)

            if not reservations:
                print("\nVous n'avez aucune réservation pour le moment.")
                return

            print("\nVoici la liste de vos réservations :")
            for res in reservations:
                # res est un objet ReservationModelOut (nouveau schéma)
                # Champs attendus : id_reservation, fk_evenement, date_reservation,
                # bus_aller, bus_retour, adherent, sam, boisson
                evt = None
                try:
                    if getattr(res, "fk_evenement", None) is not None:
                        evt = self.evenement_dao.find_by_id(res.fk_evenement)
                except Exception:
                    # On ne bloque pas l'affichage si l'événement n'est pas récupérable
                    evt = None

                print(f"\n[Réservation #{res.id_reservation}]")
                if evt is not None:
                    # evt est un EvenementModelOut : titre, date_evenement, ville, adresse, etc.
                    print(f"  Événement : {evt.titre} — le {getattr(evt, 'date_evenement', '')}")
                    ville = getattr(evt, 'ville', None)
                    adresse = getattr(evt, 'adresse', None)
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

                # Trajets bus
                print(
                    "  Trajet    : Aller? {} | Retour? {}".format(
                        "Oui" if getattr(res, "bus_aller", False) else "Non",
                        "Oui" if getattr(res, "bus_retour", False) else "Non",
                    )
                )

                # Options
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
        # Import local pour éviter la boucle circulaire
        from view.client.connexion_client_vue import ConnexionClientVue

        if not self.session.est_connecte() or not self.user:
            return ConnexionClientVue()  # Retour au menu client (connexion)

        # Menu simple pour juste revenir en arrière
        inquirer.select(
            message="Que souhaitez-vous faire ?",
            choices=["Retour au menu client"],
        ).execute()

        # Quoi qu'il arrive, on retourne au menu client
        return ConnexionClientVue()
