# view/auth/suppression_compte_vue.py
from typing import Optional
import pwinput
from dotenv import load_dotenv

from view.session import Session
from service.utilisateur_service import UtilisateurService  # Nouveau import
from model.utilisateur_models import UtilisateurModelOut
from utils.api_brevo import send_email_brevo

load_dotenv()


class SuppressionCompteVue:
    """
    Vue console de suppression de compte.
    Utilise UtilisateurService (authenticate_user, delete_user) et la Session.
    - Exige une session connectée.
    - Demande 'SUPPRIMER' + mot de passe pour confirmer.
    - Supprime via le service.
    - Envoie un e-mail de confirmation (best-effort).
    """

    def __init__(self):
        self.service = UtilisateurService()  # ✅ On remplace le DAO

    def afficher(self) -> None:
        print("\n--- SUPPRIMER MON COMPTE ---")

    def choisir_menu(self) -> Optional["AccueilVue"]:
        from view.accueil.accueil_vue import AccueilVue

        # --- Vérifie la session ---
        user: Optional[UtilisateurModelOut] = Session().utilisateur
        if user is None:
            print("⚠️ Vous devez être connecté pour supprimer votre compte.")
            return AccueilVue("Suppression annulée — retour au menu principal")

        # --- Demande de confirmation explicite ---
        print(
            "\nCette action est définitive : vos données de compte seront supprimées."
            "\nTapez exactement 'SUPPRIMER' pour confirmer."
        )
        confirmation = input("Confirmation : ").strip()
        if confirmation != "SUPPRIMER":
            print("❌ Confirmation invalide.")
            return AccueilVue("Suppression annulée — retour au menu principal")

        # --- Re-authentification avec mot de passe ---
        mot_de_passe = pwinput.pwinput(prompt="Veuillez saisir votre mot de passe : ", mask="*").strip()
        if not mot_de_passe:
            print("❌ Mot de passe requis.")
            return AccueilVue("Suppression annulée — retour au menu principal")

        try:
            reauth = self.service.authenticate_user(user.email, mot_de_passe)
            if reauth is None or reauth.id_utilisateur != user.id_utilisateur:
                print("❌ Mot de passe incorrect.")
                return AccueilVue("Suppression annulée — retour au menu principal")
        except ValueError as e:
            print(f"❌ {e}")
            return AccueilVue("Suppression annulée — retour au menu principal")
        except Exception as e:
            print(f"⚠️ Erreur technique pendant la vérification du mot de passe : {e}")
            return AccueilVue("Erreur technique — retour au menu principal")

        # --- Suppression via le service ---
        try:
            ok = self.service.delete_user(user.id_utilisateur)
            if not ok:
                print("⚠️ La suppression n’a pas été effectuée (aucune ligne affectée).")
                return AccueilVue("Suppression échouée — retour au menu principal")
        except ValueError as e:
            print(f"❌ {e}")
            return AccueilVue("Suppression annulée — retour au menu principal")
        except Exception as e:
            print(f"⚠️ Erreur technique pendant la suppression : {e}")
            return AccueilVue("Erreur technique — retour au menu principal")

        # --- Déconnexion ---
        try:
            Session().deconnexion()
            print("✅ Compte supprimé et déconnecté avec succès.")
        except Exception as e:
            print(f"(Info) Compte supprimé mais échec de la déconnexion automatique : {e}")

        # --- Envoi de l’e-mail de confirmation ---
        try:
            subject = "Confirmation de suppression de compte — BDE Ensai"
            message_text = (
                f"Bonjour {user.prenom} {user.nom},\n\n"
                "Votre compte a bien été supprimé.\n\n"
                "Si vous n'êtes pas à l'origine de cette action, contactez-nous au plus vite.\n\n"
                "— L’équipe du BDE Ensai"
            )
            status, response = send_email_brevo(
                to_email=user.email,
                subject=subject,
                message_text=message_text,
            )
            if 200 <= status < 300:
                print("📧 Un e-mail de confirmation de suppression vous a été envoyé.")
            else:
                print(f"⚠️ L'e-mail de confirmation n'a pas pu être envoyé (HTTP {status}).")
        except Exception as e:
            print(f"Impossible d'envoyer l'e-mail de confirmation : {e}")

        return AccueilVue("Compte supprimé — au revoir 👋")
