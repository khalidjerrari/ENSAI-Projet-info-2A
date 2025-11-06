from typing import Optional, Dict, Any, List
from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session
from dao.ReservationDAO import ReservationDao
from dao.Consultation_evenementDAO import ConsultationEvenementDao

# Email (Brevo) best-effort
from dotenv import load_dotenv
from utils.api_brevo import send_email_brevo
load_dotenv()


class ModificationReservationVue(VueAbstraite):
    """
    Vue console pour modifier une réservation existante de l'utilisateur connecté.
    - Liste les réservations de l'utilisateur
    - Affiche le titre de l'événement associé
    - Permet de modifier : bus_aller, bus_retour, adherent, sam, boisson
    - Met à jour via ReservationDao.update_flags(...)
    - Envoie un e-mail de confirmation (best-effort)
    """

    def __init__(self, message: str = ""):
        super().__init__(message)
        self.dao_resa = ReservationDao()
        self.dao_ev = ConsultationEvenementDao()

    # ------------- Helpers -------------
    @staticmethod
    def _flags_to_str(resa_like: Any) -> str:
        """Résumé lisible des options d'une réservation (dict ou objet)."""
        get = (lambda k, d=None: resa_like.get(k, d)) if isinstance(resa_like, dict) else (lambda k, d=None: getattr(resa_like, k, d))
        flags = []
        if get("bus_aller", False):  flags.append("Bus aller")
        if get("bus_retour", False): flags.append("Bus retour")
        if get("adherent", False):   flags.append("Adhérent")
        if get("sam", False):        flags.append("SAM")
        if get("boisson", False):    flags.append("Boisson")
        return ", ".join(flags) if flags else "Aucune option"

    def _events_title_map(self) -> Dict[int, str]:
        """Construit un mapping id_evenement -> titre (et ville/date si besoin)."""
        mapping: Dict[int, str] = {}
        try:
            evts = self.dao_ev.lister_tous(limit=1000)
            for e in evts:
                # e est un EvenementModelOut
                titre = getattr(e, "titre", "Événement")
                date_evt = getattr(e, "date_evenement", "")
                ville = getattr(e, "ville", None)
                suffix = f" — {ville}" if ville else ""
                mapping[getattr(e, "id_evenement")] = f"{date_evt} | {titre}{suffix}"
        except Exception:
            pass
        return mapping

    # ------------- Cycle Vue -------------
    def afficher(self) -> None:
        super().afficher()
        print("\n--- Modifier une réservation ---")

    def choisir_menu(self) -> Optional[VueAbstraite]:
        # Import local pour éviter les boucles
        from view.client.connexion_client_vue import ConnexionClientVue

        user = Session().utilisateur
        if not user:
            return ConnexionClientVue("Erreur : Vous n'êtes plus connecté.")

        # 1) Charger les réservations de l'utilisateur
        try:
            reservations = self.dao_resa.find_by_user(user.id_utilisateur)
        except Exception as exc:
            print(f"Erreur lors du chargement des réservations : {exc}")
            return ConnexionClientVue("Impossible de récupérer vos réservations.")

        if not reservations:
            return ConnexionClientVue("Vous n'avez aucune réservation à modifier.")

        # 2) Construire la liste affichable avec titres événements
        ev_map = self._events_title_map()
        choices: List[Dict[str, Any]] = []
        for r in reservations:
            ev_label = ev_map.get(getattr(r, "fk_evenement", None), f"Événement #{getattr(r, 'fk_evenement', '?')}")
            flags = self._flags_to_str(r)
            label = f"#{r.id_reservation} | {ev_label} | Options: {flags}"
            choices.append({"name": label, "value": r})

        choices.append({"name": "--- Retour ---", "value": None})

        # 3) Sélection de la réservation
        selection = inquirer.select(
            message="Choisissez la réservation à modifier :",
            choices=choices,
        ).execute()

        if selection is None:
            return ConnexionClientVue("Retour au menu.")

        resa = selection  # ReservationModelOut
        # Valeurs actuelles
        curr_bus_aller = bool(getattr(resa, "bus_aller", False))
        curr_bus_retour = bool(getattr(resa, "bus_retour", False))
        curr_adherent = bool(getattr(resa, "adherent", False))
        curr_sam = bool(getattr(resa, "sam", False))
        curr_boisson = bool(getattr(resa, "boisson", False))

        # 4) Demander les nouvelles valeurs (defaults = actuelles)
        new_bus_aller = inquirer.confirm(message="Bus ALLER ?", default=curr_bus_aller, amark="✓").execute()
        new_bus_retour = inquirer.confirm(message="Bus RETOUR ?", default=curr_bus_retour, amark="✓").execute()
        new_adherent = inquirer.confirm(message="Êtes-vous adhérent ?", default=curr_adherent, amark="✓").execute()
        new_sam = inquirer.confirm(message="Êtes-vous SAM ce soir ?", default=curr_sam, amark="✓").execute()
        new_boisson = inquirer.confirm(message="Prenez-vous une boisson ?", default=curr_boisson, amark="✓").execute()

        # 5) Si rien n'a changé -> message et retour
        if (
            new_bus_aller == curr_bus_aller and
            new_bus_retour == curr_bus_retour and
            new_adherent == curr_adherent and
            new_sam == curr_sam and
            new_boisson == curr_boisson
        ):
            return ConnexionClientVue("Aucun changement détecté.")

        # 6) Confirmation
        confirme = inquirer.confirm(message="Appliquer les modifications ?", default=True, amark="✓").execute()
        if not confirme:
            return ConnexionClientVue("Modification annulée.")

        # 7) Mise à jour via DAO
        try:
            updated = self.dao_resa.update_flags(
                resa.id_reservation,
                bus_aller=new_bus_aller,
                bus_retour=new_bus_retour,
                adherent=new_adherent,
                sam=new_sam,
                boisson=new_boisson,
            )
            if not updated:
                return ConnexionClientVue("Échec de la modification de la réservation.")
        except Exception as exc:
            print(f"Erreur lors de la mise à jour : {exc}")
            return ConnexionClientVue("Échec de la modification de la réservation.")

        # 8) E-mail de confirmation (best-effort)
        try:
            ev_label = self._events_title_map().get(getattr(resa, "fk_evenement", None), f"Événement #{getattr(resa, 'fk_evenement', '?')}")
            options = []
            if new_bus_aller:  options.append("Bus aller")
            if new_bus_retour: options.append("Bus retour")
            if new_adherent:   options.append("Adhérent")
            if new_sam:        options.append("SAM")
            if new_boisson:    options.append("Boisson")
            options_str = ", ".join(options) if options else "Aucune option"

            subject = "Modification de votre réservation — BDE Ensai"
            message_text = (
                f"Bonjour {user.prenom} {user.nom},\n\n"
                f"Les options de votre réservation #{resa.id_reservation} ont été mises à jour.\n\n"
                f"{ev_label}\n"
                f"Nouvelles options : {options_str}\n\n"
                "Si vous n'êtes pas à l'origine de cette action, merci de nous contacter.\n\n"
                "— L’équipe du BDE Ensai"
            )
            status, response = send_email_brevo(
                to_email=user.email,
                subject=subject,
                message_text=message_text,
            )
            if 200 <= status < 300:
                print("Un e-mail de confirmation de modification vous a été envoyé.")
            else:
                print(f"E-mail non envoyé (HTTP {status}).")
        except Exception as exc:
            print(f"Impossible d'envoyer l'e-mail de confirmation : {exc}")

        return ConnexionClientVue("Réservation modifiée avec succès.")
