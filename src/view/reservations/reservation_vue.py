from typing import Optional, Any, Dict, List
from datetime import date
from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session
from dao.ReservationDAO import ReservationDao
from dao.Consultation_evenementDAO import ConsultationEvenementDao
from model.reservation_models import ReservationModelIn

# ➕ Ajout pour l'e-mail
from dotenv import load_dotenv
from utils.api_brevo import send_email_brevo
load_dotenv()


class ReservationVue(VueAbstraite):
    def __init__(self, evenement: Any, message: str = ""):
        super().__init__(message)
        self.dao_resa = ReservationDao()
        self.dao_ev = ConsultationEvenementDao()

        self._evenement_orig = evenement
        self.id_evenement: Optional[int] = self._extract_id_evenement(evenement)
        self.evenement = self._fetch_evenement(self.id_evenement)

    @staticmethod
    def _extract_id_evenement(evenement: Any) -> Optional[int]:
        if evenement is None:
            return None
        if isinstance(evenement, dict):
            return evenement.get("id_evenement") or evenement.get("id") or None
        return getattr(evenement, "id_evenement", None) or getattr(evenement, "id", None)

    @staticmethod
    def _get_attr(ev: Any, key: str, default=None):
        if ev is None:
            return default
        if isinstance(ev, dict):
            return ev.get(key, default)
        return getattr(ev, key, default)

    def _fetch_evenement(self, id_evenement: Optional[int]):
        if not id_evenement:
            return None
        try:
            dispo = self.dao_ev.lister_avec_places_restantes(limit=200, a_partir_du=date.today())
            for row in dispo:
                if row.get("id_evenement") == id_evenement:
                    return row
        except Exception:
            pass
        try:
            tous = self.dao_ev.lister_tous(limit=500)
            for ev in tous:
                if getattr(ev, "id_evenement", None) == id_evenement:
                    return ev
        except Exception:
            pass
        return self._evenement_orig

    def afficher(self):
        super().afficher()
        user = Session().utilisateur
        if not user:
            print("Erreur : Vous n'êtes plus connecté.")
            return
        if not self.id_evenement or not self.evenement:
            print("Erreur : Aucun événement sélectionné.")
            return

        titre = self._get_attr(self.evenement, "titre", "N/A")
        date_evt = self._get_attr(self.evenement, "date_evenement", "N/A")
        ville = self._get_attr(self.evenement, "ville")
        adresse = self._get_attr(self.evenement, "adresse")
        lieu = ville or adresse or "N/A"

        capacite = self._get_attr(self.evenement, "capacite")
        places_restantes = self.evenement.get("places_restantes") if isinstance(self.evenement, dict) else None

        capa_str = f" | Capacité : {capacite}" if capacite is not None else ""
        places_str = f" | Places restantes : {places_restantes}" if places_restantes is not None else ""

        print(f"--- ✅ Confirmer la réservation ---")
        print(f"Événement : {titre}")
        print(f"Date      : {date_evt}")
        print(f"Lieu      : {lieu}{capa_str}{places_str}")

    def choisir_menu(self) -> Optional[VueAbstraite]:
        from view.client.connexion_client_vue import ConnexionClientVue

        user = Session().utilisateur
        if not user or not self.id_evenement:
            return ConnexionClientVue("Erreur lors de la réservation.")

        try:
            # Saisie des options
            bus_aller  = inquirer.confirm(message="Souhaitez-vous le bus ALLER ?",  default=False, amark="✓").execute()
            bus_retour = inquirer.confirm(message="Souhaitez-vous le bus RETOUR ?", default=False, amark="✓").execute()
            adherent   = inquirer.confirm(message="Êtes-vous adhérent ?",           default=False, amark="✓").execute()
            sam        = inquirer.confirm(message="Êtes-vous SAM ce soir ?",        default=False, amark="✓").execute()
            boisson    = inquirer.confirm(message="Prenez-vous une boisson ?",      default=False, amark="✓").execute()
            confirme   = inquirer.confirm(message="Confirmer la réservation ?",      default=True,  amark="✓").execute()

            if not confirme:
                return ConnexionClientVue("Réservation annulée.")

            reservation_in = ReservationModelIn(
                fk_utilisateur=user.id_utilisateur,
                fk_evenement=self.id_evenement,
                bus_aller=bus_aller,
                bus_retour=bus_retour,
                adherent=adherent,
                sam=sam,
                boisson=boisson,
            )

            nouvelle_reservation = self.dao_resa.create(reservation_in)

            if nouvelle_reservation:
                # ------- ENVOI EMAIL DE CONFIRMATION (best-effort) -------
                try:
                    titre = self._get_attr(self.evenement, "titre", "N/A")
                    date_evt = self._get_attr(self.evenement, "date_evenement", "N/A")
                    ville = self._get_attr(self.evenement, "ville")
                    adresse = self._get_attr(self.evenement, "adresse")
                    lieu = ville or adresse or "Lieu non renseigné"

                    subject = "Confirmation de réservation — BDE Ensai"
                    options = []
                    if bus_aller:  options.append("Bus aller")
                    if bus_retour: options.append("Bus retour")
                    if adherent:   options.append("Adhérent")
                    if sam:        options.append("SAM")
                    if boisson:    options.append("Boisson")
                    options_str = ", ".join(options) if options else "Aucune option"

                    message_text = (
                        f"Bonjour {user.prenom} {user.nom},\n\n"
                        f"Votre réservation #{nouvelle_reservation.id_reservation} a bien été enregistrée.\n\n"
                        f"Événement : {titre}\n"
                        f"Date      : {date_evt}\n"
                        f"Lieu      : {lieu}\n"
                        f"Options   : {options_str}\n\n"
                        "Si vous n'êtes pas à l'origine de cette action, merci de nous contacter.\n\n"
                        "— L’équipe du BDE Ensai"
                    )

                    status, response = send_email_brevo(
                        to_email=user.email,
                        subject=subject,
                        message_text=message_text,
                    )
                    if 200 <= status < 300:
                        print("📧 Un e-mail de confirmation vous a été envoyé.")
                    else:
                        print(f"⚠️  Attention : l'e-mail de confirmation n'a pas pu être envoyé (HTTP {status}).")
                except Exception as exc:
                    print(f"⚠️  Impossible d'envoyer l'e-mail de confirmation : {exc}")
                # --------------------------------------------------------

                msg = f"🎉 Réservation #{nouvelle_reservation.id_reservation} confirmée pour cet événement !"
            else:
                msg = "❌ Échec. Vous avez peut-être déjà une réservation enregistrée."

            return ConnexionClientVue(msg)

        except Exception as e:
            print(f"Erreur inattendue : {e}")
            return ConnexionClientVue("Une erreur est survenue.")
