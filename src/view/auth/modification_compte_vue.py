# view/auth/modification_compte_vue.py
from typing import Optional, List
import re

from pydantic import ValidationError

from view.session import Session
from dao.UtilisateurDAO import UtilisateurDao
from model.utilisateur_models import UtilisateurModelOut

from dotenv import load_dotenv
from utils.api_brevo import send_email_brevo
import pwinput

load_dotenv()


class ModificationCompteVue:
    """
    Vue console de modification de compte.
    - Exige une session connectée.
    - Permet de modifier nom, prénom, téléphone, email.
    - Vérifie l'unicité de l'email si modifié.
    - Option de changement de mot de passe avec re-authentification.
    - Met à jour via UtilisateurDao.update et UtilisateurDao.change_password.
    - Envoie des e-mails de notification (best-effort).
    """

    def __init__(self, dao: Optional[UtilisateurDao] = None):
        self.dao = dao or UtilisateurDao()

    def afficher(self) -> None:
        print("\n--- MODIFIER MON COMPTE ---")

    def choisir_menu(self) -> Optional["AccueilVue"]:
        from view.accueil.accueil_vue import AccueilVue

        # --- Doit être connecté ---
        current: Optional[UtilisateurModelOut] = Session().utilisateur
        if current is None:
            print("Vous devez être connecté pour modifier votre compte.")
            return AccueilVue("Modification annulée — retour au menu principal")

        # --- Saisie avec valeurs par défaut (laisser vide pour conserver) ---
        print("Laissez vide pour garder la valeur actuelle.")
        nom = input(f"Nom [{current.nom}] : ").strip() or current.nom
        prenom = input(f"Prénom [{current.prenom}] : ").strip() or current.prenom
        tel_prompt = current.telephone or ""
        telephone = input(f"Téléphone (optionnel) [{tel_prompt}] : ").strip() or current.telephone
        email = input(f"Email [{current.email}] : ").strip() or current.email

        # --- Vérifs simples (feedback immédiat) ---
        erreurs = self._verifs_preliminaires_modif(
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            email=email,
        )
        if erreurs:
            print("\n Erreurs :")
            for e in erreurs:
                print(f" - {e}")
            return AccueilVue("Modification annulée — retour au menu principal")

        # --- Unicité email si modifié ---
        if email != current.email:
            try:
                existing = self.dao.find_by_email(email)
                if existing is not None and existing.id_utilisateur != current.id_utilisateur:
                    print("Un compte existe déjà avec cet email.")
                    return AccueilVue("Modification annulée — retour au menu principal")
            except Exception as exc:
                print(f"Erreur technique lors de la vérification de l'email : {exc}")
                return AccueilVue("Erreur technique — retour au menu principal")

        # --- Construction d'un UtilisateurModelOut pour update ---
        try:
            # On conserve id_utilisateur & date_creation depuis la session
            updated_candidate = UtilisateurModelOut(
                id_utilisateur=current.id_utilisateur,
                email=email,
                prenom=prenom,
                nom=nom,
                telephone=telephone,
                administrateur=getattr(current, "administrateur", False),
                date_creation=current.date_creation,
            )
        except ValidationError as ve:
            print("\n Données invalides :")
            for err in ve.errors():
                loc = ".".join(str(x) for x in err.get("loc", []))
                msg = err.get("msg", "invalide")
                print(f" - {loc}: {msg}")
            return AccueilVue("Modification annulée — retour au menu principal")

        # --- Persistance via DAO.update ---
        try:
            user_out = self.dao.update(updated_candidate)
            if user_out is None:
                print("La mise à jour a échoué (aucune ligne affectée).")
                return AccueilVue("Modification échouée — retour au menu principal")
        except Exception as exc:
            print(f"Erreur lors de la mise à jour du compte : {exc}")
            return AccueilVue("Modification échouée — retour au menu principal")

        # --- Rafraîchir la session ---
        try:
            Session().connexion(user_out)
            print("Profil mis à jour.")
        except Exception as exc:
            print(f"(Info) Profil mis à jour mais échec de la mise à jour de session : {exc}")

        # --- Option : changement de mot de passe ---
        try:
            changer_mdp = input("Souhaitez-vous changer votre mot de passe ? (o/N) : ").strip().lower()
        except Exception:
            changer_mdp = "n"

        if changer_mdp == "o":
            # Re-authentification
            mot_de_passe_actuel = pwinput.pwinput(prompt="Mot de passe actuel: ", mask="*").strip()
            try:
                reauth = self.dao.authenticate(user_out.email, mot_de_passe_actuel)
                if reauth is None or reauth.id_utilisateur != user_out.id_utilisateur:
                    print("Échec de la re-authentification (mot de passe incorrect).")
                    return AccueilVue("Modification partielle : profil OK, mot de passe non changé — retour au menu principal")
            except Exception as exc:
                print(f"Erreur technique lors de la vérification du mot de passe : {exc}")
                return AccueilVue("Erreur technique — retour au menu principal")

            # Saisie nouveau mot de passe
            new_pwd =  pwinput.pwinput(prompt="Nouveau mot de passe : ", mask="*")
            new_pwd2 = pwinput.pwinput(prompt="Confirmez le nouveau mot de passe : ", mask="*")

            pwd_errs = self._verifs_password_change(new_pwd, new_pwd2)
            if pwd_errs:
                print("\n Erreurs :")
                for e in pwd_errs:
                    print(f" - {e}")
                return AccueilVue("Modification partielle : profil OK, mot de passe non changé — retour au menu principal")

            # Persistance du nouveau mot de passe
            try:
                ok = self.dao.change_password(user_out.id_utilisateur, new_pwd)
                if not ok:
                    print("Le mot de passe n'a pas été modifié (aucune ligne affectée).")
                    return AccueilVue("Modification partielle : profil OK, mot de passe non changé — retour au menu principal")
                print("Mot de passe mis à jour.")
            except Exception as exc:
                print(f"Erreur lors du changement de mot de passe : {exc}")
                return AccueilVue("Modification partielle : profil OK, mot de passe non changé — retour au menu principal")

            # E-mail de notification de changement de mot de passe (best-effort)
            try:
                subject = "Votre mot de passe a été modifié — BDE Ensai"
                message_text = (
                    f"Bonjour {user_out.prenom} {user_out.nom},\n\n"
                    "Votre mot de passe vient d'être modifié.\n"
                    "Si vous n'êtes pas à l'origine de cette action, contactez-nous immédiatement.\n\n"
                    "— L’équipe du BDE Ensai"
                )
                status, response = send_email_brevo(
                    to_email=user_out.email,
                    subject=subject,
                    message_text=message_text,
                )
                if 200 <= status < 300:
                    print("Un e-mail de confirmation de changement de mot de passe vous a été envoyé.")
                else:
                    print(f"Attention : l'e-mail de confirmation n'a pas pu être envoyé (HTTP {status}).")
            except Exception as exc:
                print(f"Impossible d'envoyer l'e-mail de confirmation (mot de passe) : {exc}")

        # --- E-mail de confirmation de modification de profil (best-effort) ---
        try:
            subject = "Votre profil a été mis à jour — BDE Ensai"
            message_text = (
                f"Bonjour {user_out.prenom} {user_out.nom},\n\n"
                "Les informations de votre profil ont été mises à jour avec succès.\n"
                "Si vous n'êtes pas à l'origine de cette action, veuillez nous contacter.\n\n"
                "— L’équipe du BDE Ensai"
            )
            status, response = send_email_brevo(
                to_email=user_out.email,
                subject=subject,
                message_text=message_text,
            )
            if 200 <= status < 300:
                print("Un e-mail de confirmation de modification de profil vous a été envoyé.")
            else:
                print(f"Attention : l'e-mail de confirmation n'a pas pu être envoyé (HTTP {status}).")
        except Exception as exc:
            print(f"Impossible d'envoyer l'e-mail de confirmation (profil) : {exc}")

        return AccueilVue("Profil mis à jour — retour au menu principal")

    # =========================
    # Helpers validations simples
    # =========================
    def _verifs_preliminaires_modif(
        self,
        nom: str,
        prenom: str,
        telephone: Optional[str],
        email: str,
    ) -> List[str]:
        erreurs: List[str] = []
        if not nom:
            erreurs.append("Le nom est obligatoire.")
        if not prenom:
            erreurs.append("Le prénom est obligatoire.")
        if telephone and not self._telephone_valide(telephone):
            erreurs.append("Téléphone invalide (10 chiffres, ex. 0601020304).")
        if not self._email_rough_check(email):
            erreurs.append("Format d'email suspect.")
        return erreurs

    def _verifs_password_change(self, pwd: str, pwd2: str) -> List[str]:
        erreurs: List[str] = []
        if pwd != pwd2:
            erreurs.append("Les mots de passe ne correspondent pas.")
        if not self._password_valide(pwd):
            erreurs.append("Mot de passe trop faible (min 8, avec lettre et chiffre).")
        return erreurs

    @staticmethod
    def _email_rough_check(email: str) -> bool:
        return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))

    @staticmethod
    def _telephone_valide(tel: str) -> bool:
        tel_numbers = re.sub(r"[ \.\-]", "", tel)
        return bool(re.match(r"^\d{10}$", tel_numbers))

    @staticmethod
    def _password_valide(pwd: str) -> bool:
        if len(pwd) < 8:
            return False
        if not re.search(r"[A-Za-z]", pwd):
            return False
        if not re.search(r"\d", pwd):
            return False
        return True
