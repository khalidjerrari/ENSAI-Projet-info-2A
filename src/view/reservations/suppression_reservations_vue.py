# src/view/reservations/suppression_reservation_vue.py
from typing import Optional, Any, Dict, List
from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session

# ✅ Passage à la couche service
from service.reservation_service import ReservationService
from service.evenement_service import EvenementService

# ✅ Envoi d'e-mail (Brevo)
from dotenv import load_dotenv
from utils.api_brevo import send_email_brevo
load_dotenv()


class SuppressionReservationVue(VueAbstraite):
    """
    Vue console pour supprimer une réservation de l'utilisateur connecté.

    ✅ Refactorisée pour utiliser la couche service :
      - `ReservationService` pour les opérations CRUD
      - `EvenementService` pour les infos associées
      - Plus de dépendance directe aux DAO
    """

    def __init__(self, message: str = "", reservation: Any = None):
        super().__init__(message)
        self.reservation_service = ReservationService()
        self.evenement_service = EvenementService()
        self._reservation_preselectionnee = reservation

    # ----------------- Helpers -----------------
    @staticmethod
    def _flags_to_str(resa_like: Any) -> str:
        """Résumé lisible des options d'une réservation."""
        flags = []
        if getattr(resa_like, "bus_aller", False):  flags.append("Bus aller")
        if getattr(resa_like, "bus_retour", False): flags.append("Bus retour")
        if getattr(resa_like, "adherent", False):   flags.append("Adhérent")
        if getattr(resa_like, "sam", False):        flags.append("SAM")
        if getattr(resa_like, "boisson", False):    flags.append("Boisson")
        return ", ".join(flags) if flags else "Aucune option"

    def _event_label(self, fk_evenement: Optional[int]) -> str:
        """Retourne un libellé lisible de l'événement lié à la réservation."""
        if not fk_evenement:
            return "Événement inconnu"
        try:
            evt = self.evenement_service.get_evenement_by_id(fk_evenement)
            if evt:
                ville = getattr(evt, "ville", None)
                suffix = f" — {ville}" if ville else ""
                return f"{getattr(evt, 'date_evenement', '')} | {evt.titre}{suffix}"
        except Exception:
            pass
        return f"Événement #{fk_evenement}"

    # ----------------- Cycle Vue -----------------
    def afficher(self) -> None:
        """
        Affiche l’en-tête indiquant la suppression d’une réservation.
        """
        super().afficher()
        print("\n--- 🗑️  Supprimer une réservation ---")

    def choisir_menu(self) -> Optional[VueAbstraite]:
        """
        Permet à l’utilisateur de sélectionner et confirmer la suppression d’une réservation.
        """
        # Import local pour éviter les boucles circulaires
        from view.client.connexion_client_vue import ConnexionClientVue

        user = Session().utilisateur
        if not user:
            return ConnexionClientVue("Erreur : vous n'êtes pas connecté.")

        # 1️⃣ Déterminer la réservation à supprimer
        resa = self._reservation_preselectionnee
        if resa is None:
            try:
                reservations = self.reservation_service.get_reservations_by_user(user.id_utilisateur)
            except Exception as exc:
                print(f"Erreur lors du chargement des réservations : {exc}")
                return ConnexionClientVue("Impossible de récupérer vos réservations.")

            if not reservations:
                return ConnexionClientVue("Vous n'avez aucune réservation à supprimer.")

            # Construire le menu
            choices: List[Dict[str, Any]] = []
            for r in reservations:
                ev_label = self._event_label(getattr(r, "fk_evenement", None))
                flags = self._flags_to_str(r)
                label = f"#{r.id_reservation} | {ev_label} | Options: {flags}"
                choices.append({"name": label, "value": r})
            choices.append({"name": "--- Retour ---", "value": None})

            resa = inquirer.select(
                message="Sélectionnez la réservation à supprimer :",
                choices=choices,
            ).execute()

            if resa is None:
                return ConnexionClientVue("Suppression annulée.")

        # 2️⃣ Récapitulatif
        ev_label = self._event_label(getattr(resa, "fk_evenement", None))
        print("\nVous allez supprimer la réservation suivante :")
        print(f"  • Réservation #{resa.id_reservation}")
        print(f"  • {ev_label}")
        print(f"  • Options : {self._flags_to_str(resa)}")

        # 3️⃣ Double confirmation
        confirme = inquirer.confirm(
            message="Confirmer la suppression de cette réservation ?",
            default=False,
            amark="✓",
        ).execute()
        if not confirme:
            return ConnexionClientVue("Suppression annulée.")

        saisie = inquirer.text(
            message="Tapez 'SUPPRIMER' pour confirmer (ou Entrée pour annuler) :"
        ).execute()
        if saisie.strip().upper() != "SUPPRIMER":
            return ConnexionClientVue("Suppression annulée.")

        # 4️⃣ Suppression via le service
        try:
            ok = self.reservation_service.delete_reservation(resa.id_reservation)
            if not ok:
                return ConnexionClientVue("❌ Échec de la suppression (aucune ligne affectée).")
        except Exception as exc:
            print(f"Erreur lors de la suppression : {exc}")
            return ConnexionClientVue("❌ Échec de la suppression de la réservation.")

        # 5️⃣ E-mail de confirmation (best-effort)
        try:
            subject = "Annulation de réservation — BDE Ensai"
            message_text = (
                f"Bonjour {user.prenom} {user.nom},\n\n"
                f"Votre réservation #{resa.id_reservation} a été supprimée.\n"
                f"Détails : {ev_label}\n\n"
                "Si vous n'êtes pas à l'origine de cette action, merci de nous contacter.\n\n"
                "— L’équipe du BDE Ensai"
            )
            status, _ = send_email_brevo(
                to_email=user.email,
                subject=subject,
                message_text=message_text,
            )
            if 200 <= status < 300:
                print("📧 Un e-mail de confirmation d'annulation vous a été envoyé.")
            else:
                print(f"⚠️  E-mail non envoyé (HTTP {status}).")
        except Exception as exc:
            print(f"⚠️  Impossible d'envoyer l'e-mail de confirmation : {exc}")

        return ConnexionClientVue("✅ Réservation supprimée avec succès.")
