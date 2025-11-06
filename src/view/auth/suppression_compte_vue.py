# view/auth/suppression_compte_vue.py
from typing import Optional

from pydantic import ValidationError  # cohérence imports (même si non utilisé ici)

from view.session import Session
from dao.UtilisateurDAO import UtilisateurDao
from model.utilisateur_models import UtilisateurModelOut

from dotenv import load_dotenv
from utils.api_brevo import send_email_brevo

load_dotenv()


class SuppressionCompteVue:
    """
    Vue console de suppression de compte.
    Utilise UtilisateurDao (authenticate, delete) et la Session.
    - Exige une session connectée.
    - Demande 'SUPPRIMER' + mot de passe pour confirmer.
    - Supprime via DAO.
    - Envoie un e-mail de confirmation (best-effort).
    """

    def __init__(self, dao: Optional[UtilisateurDao] = None):
        self.dao = dao or UtilisateurDao()

    def afficher(self) -> None:
        print("\n--- SUPPRIMER MON COMPTE ---")

    def choisir_menu(self) -> Optional["AccueilVue"]:
        from view.accueil.accueil_vue import AccueilVue

        # --- Doit être connecté ---
        user: Optional[UtilisateurModelOut] = Session().utilisateur
        if user is None:
            print("Vous devez être connecté pour supprimer votre compte.")
            return AccueilVue("Suppression annulée — retour au menu principal")

        # --- Rappel des conséquences + confirmation explicite ---
        print(
            "\nCette action est définitive : vos données de compte seront supprimées."
            "\nTapez exactement 'SUPPRIMER' pour confirmer."
        )
        confirmation = input("Confirmation : ").strip()
        if confirmation != "SUPPRIMER":
            print("Confirmation invalide.")
            return AccueilVue("Suppression annulée — retour au menu principal")

        # --- Re-authentification via mot de passe ---
        mot_de_passe = input("Veuillez saisir votre mot de passe : ").strip()
        if not mot_de_passe:
            print("Mot de passe requis.")
            return AccueilVue("Suppression annulée — retour au menu principal")

        try:
            reauth = self.dao.authenticate(user.email, mot_de_passe)
            if reauth is None or reauth.id_utilisateur != user.id_utilisateur:
                print("Échec de la re-authentification (mot de passe incorrect).")
                return AccueilVue("Suppression annulée — retour au menu principal")
        except Exception as exc:
            print(f"Erreur technique lors de la vérification du mot de passe : {exc}")
            return AccueilVue("Erreur technique — retour au menu principal")

        # --- Suppression via DAO ---
        try:
            ok = self.dao.delete(user.id_utilisateur)
            if not ok:
                print("La suppression n'a pas été effectuée (aucune ligne affectée).")
                return AccueilVue("Suppression échouée — retour au menu principal")
        except Exception as exc:
            print(f"Erreur lors de la suppression du compte : {exc}")
            return AccueilVue("Suppression échouée — retour au menu principal")

        # --- Déconnexion de la session (best-effort) ---
        try:
            Session().deconnexion()
        except Exception as exc:
            print(f"(Info) Compte supprimé mais échec de la déconnexion automatique : {exc}")

        # --- E-mail de confirmation (best-effort) ---
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
                print("Un e-mail de confirmation de suppression vous a été envoyé.")
            else:
                print(f"Attention : l'e-mail de confirmation n'a pas pu être envoyé (HTTP {status}).")
        except Exception as exc:
            print(f"Impossible d'envoyer l'e-mail de confirmation : {exc}")

        return AccueilVue("Compte supprimé — au revoir 👋")
