# src/view/reservations/reservation_vue.py
from typing import Optional, Any
from datetime import date
from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session

# ✅ Passage aux services
from service.reservation_service import ReservationService
from service.evenement_service import EvenementService
from model.reservation_models import ReservationModelIn

# ➕ Envoi d’e-mail de confirmation
from dotenv import load_dotenv
from utils.api_brevo import send_email_brevo
load_dotenv()


class ReservationVue(VueAbstraite):
    """
    Vue console : permet à un utilisateur de réserver une place pour un événement.
    - Utilise ReservationService et EvenementService.
    - Envoie un e-mail de confirmation (best-effort).
    """

    def __init__(self, message: str = "", evenement: Optional[Any] = None):
        super().__init__(message)
        self.session = Session()
        self.user = self.session.utilisateur
        self.reservation_service = ReservationService()
        self.evenement_service = EvenementService()
        self.evenement = evenement

    # ----------------- Cycle Vue -----------------
    def afficher(self) -> None:
        super().afficher()
        print("\n--- 🎟️ Réservation d’un événement ---")

    def choisir_menu(self) -> Optional[VueAbstraite]:
        from view.client.connexion_client_vue import ConnexionClientVue
        from view.consulter.consulter_evenement_vue import ConsulterVue

        # --- Vérification de la connexion ---
        if not self.session.est_connecte() or not self.user:
            print("⛔ Vous devez être connecté pour réserver.")
            return ConsulterVue("Connexion requise pour réserver.")

        # --- Étape 1 : sélectionner ou confirmer l’événement ---
        if not self.evenement:
            evenements = self.evenement_service.lister_evenements_disponibles()
            if not evenements:
                print("Aucun événement disponible pour réservation.")
                return ConsulterVue("Aucun événement disponible.")

            choix_evt = inquirer.select(
                message="Sélectionnez un événement :",
                choices=[
                    {"name": f"{e.date_evenement} | {e.titre}", "value": e}
                    for e in evenements
                ] + [{"name": "--- Retour ---", "value": None}],
            ).execute()

            if choix_evt is None:
                return ConsulterVue("Retour au menu précédent.")
            self.evenement = choix_evt

        evt = self.evenement
        print(f"\nÉvénement sélectionné : {evt.titre} ({evt.date_evenement})")

        # --- Étape 2 : vérifier les places restantes ---
        if hasattr(evt, "places_restantes") and evt.places_restantes == 0:
            print("⚠️  L'événement est complet.")
            return ConsulterVue("Événement complet.")

        # --- Étape 3 : saisie des options de réservation ---
        print("\n--- Choix de vos options ---")
        bus_aller = inquirer.confirm(message="Souhaitez-vous un bus ALLER ?", default=True).execute()
        bus_retour = inquirer.confirm(message="Souhaitez-vous un bus RETOUR ?", default=True).execute()
        adherent = inquirer.confirm(message="Êtes-vous adhérent ?", default=False).execute()
        sam = inquirer.confirm(message="Êtes-vous SAM ?", default=False).execute()
        boisson = inquirer.confirm(message="Souhaitez-vous une boisson ?", default=False).execute()

        # --- Étape 4 : construction du modèle ---
        resa_in = ReservationModelIn(
            fk_utilisateur=self.user.id_utilisateur,
            fk_evenement=evt.id_evenement,
            date_reservation=date.today(),
            bus_aller=bus_aller,
            bus_retour=bus_retour,
            adherent=adherent,
            sam=sam,
            boisson=boisson,
        )

        # --- Étape 5 : enregistrement via le service ---
        try:
            resa_out = self.reservation_service.create_reservation(resa_in)
        except Exception as e:
            print(f"❌ Erreur lors de la création de la réservation : {e}")
            return ConnexionClientVue("Erreur lors de la réservation.")

        if not resa_out:
            print("❌ La réservation n’a pas pu être créée (peut-être déjà existante ?).")
            return ConnexionClientVue("Échec de la réservation.")

        print(f"✅ Réservation confirmée pour {evt.titre} ({evt.date_evenement})")

        # --- Étape 6 : e-mail de confirmation ---
        try:
            subject = "Confirmation de votre réservation — BDE Ensai"
            message_text = (
                f"Bonjour {self.user.prenom} {self.user.nom},\n\n"
                f"Votre réservation pour l’événement « {evt.titre} » du {evt.date_evenement} est confirmée.\n\n"
                f"Options :\n"
                f" - Bus aller : {'Oui' if bus_aller else 'Non'}\n"
                f" - Bus retour : {'Oui' if bus_retour else 'Non'}\n"
                f" - Adhérent : {'Oui' if adherent else 'Non'}\n"
                f" - SAM : {'Oui' if sam else 'Non'}\n"
                f" - Boisson : {'Oui' if boisson else 'Non'}\n\n"
                "Si vous n’êtes pas à l’origine de cette action, veuillez nous contacter.\n\n"
                "— L’équipe du BDE Ensai"
            )

            status, _ = send_email_brevo(
                to_email=self.user.email,
                subject=subject,
                message_text=message_text,
            )

            if 200 <= status < 300:
                print("📧 Un e-mail de confirmation vous a été envoyé.")
            else:
                print(f"⚠️  E-mail non envoyé (HTTP {status}).")

        except Exception as exc:
            print(f"⚠️ Impossible d'envoyer l'e-mail de confirmation : {exc}")

        # --- Étape 7 : retour au menu client ---
        return ConnexionClientVue("Réservation effectuée avec succès.")
