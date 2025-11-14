# view/auth/modification_compte_vue.py
from typing import Optional, List
import re
import pwinput
from pydantic import ValidationError
from dotenv import load_dotenv

from view.session import Session
from service.utilisateur_service import UtilisateurService  # Nouveau import
from model.utilisateur_models import UtilisateurModelOut
from utils.api_brevo import send_email_brevo

load_dotenv()


class ModificationCompteVue:
    """
    Vue console de modification de compte.
    - Exige une session connectée.
    - Utilise UtilisateurService pour la logique métier.
    - Permet de modifier nom, prénom, téléphone, email et mot de passe.
    - Envoie des e-mails de confirmation (best-effort).
    """

    def __init__(self):
        self.service = UtilisateurService()  # Remplace le DAO

    def afficher(self) -> None:
        print("\n--- MODIFIER MON COMPTE ---")

    def choisir_menu(self) -> Optional["AccueilVue"]:
        from view.accueil.accueil_vue import AccueilVue

        # --- Vérifie la connexion ---
        current: Optional[UtilisateurModelOut] = Session().utilisateur
        if current is None:
            print("⚠️ Vous devez être connecté pour modifier votre compte.")
            return AccueilVue("Modification annulée — retour au menu principal")

        # --- Saisie avec valeurs actuelles ---
        print("Laissez vide pour conserver la valeur actuelle.")
        nom = input(f"Nom [{current.nom}] : ").strip() or current.nom
        prenom = input(f"Prénom [{current.prenom}] : ").strip() or current.prenom
        tel_prompt = current.telephone or ""
        telephone = input(f"Téléphone (optionnel) [{tel_prompt}] : ").strip() or current.telephone
        email = input(f"Email [{current.email}] : ").strip() or current.email

        # --- Vérifs préliminaires ---
        erreurs = self._verifs_preliminaires_modif(nom, prenom, telephone, email)
        if erreurs:
            print("\nErreurs :")
            for e in erreurs:
                print(f" - {e}")
            return AccueilVue("Modification annulée — retour au menu principal")

        # --- Vérifie si l’email est déjà pris (si modifié) ---
        if email != current.email:
            existing = self.service.get_user_by_email(email)
            if existing and existing.id_utilisateur != current.id_utilisateur:
                print("Un compte existe déjà avec cet email.")
                return AccueilVue("Modification annulée — retour au menu principal")

        # --- Construction du modèle de mise à jour ---
        try:
            updated_user = UtilisateurModelOut(
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

        # --- Mise à jour via le service ---
        try:
            user_out = self.service.update_user(updated_user)
        except ValueError as e:
            print(f"{e}")
            return AccueilVue("Modification échouée — retour au menu principal")
        except Exception as e:
            print(f"⚠️ Erreur technique : {e}")
            return AccueilVue("Modification échouée — retour au menu principal")

        # --- Rafraîchit la session ---
        Session().connexion(user_out)
        print("Profil mis à jour avec succès.")

        # --- Option : changement de mot de passe ---
        changer_mdp = input("Souhaitez-vous changer votre mot de passe ? (o/N) : ").strip().lower()
        if changer_mdp == "o":
            mot_de_passe_actuel = pwinput.pwinput(prompt="Mot de passe actuel: ", mask="*").strip()
            try:
                reauth = self.service.authenticate_user(email=user_out.email, password=mot_de_passe_actuel)
                if reauth is None or reauth.id_utilisateur != user_out.id_utilisateur:
                    print("Échec de la re-authentification (mot de passe incorrect).")
                    return AccueilVue("Profil mis à jour — mot de passe non changé.")
            except Exception as exc:
                print(f"Erreur technique lors de la vérification du mot de passe : {exc}")
                return AccueilVue("Erreur technique — retour au menu principal")

            new_pwd = pwinput.pwinput(prompt="Nouveau mot de passe : ", mask="*")
            new_pwd2 = pwinput.pwinput(prompt="Confirmez le nouveau mot de passe : ", mask="*")
            pwd_errs = self._verifs_password_change(new_pwd, new_pwd2)
            if pwd_errs:
                print("\n Erreurs :")
                for e in pwd_errs:
                    print(f" - {e}")
                return AccueilVue("Profil mis à jour — mot de passe non changé.")

            try:
                ok = self.service.change_user_password(user_out.id_utilisateur, new_pwd)
                if not ok:
                    print("Le mot de passe n’a pas pu être modifié.")
                else:
                    print("✅ Mot de passe mis à jour.")
                    self._send_mail_notification(
                        user_out.email,
                        user_out.prenom,
                        user_out.nom,
                        "Votre mot de passe a été modifié — BDE Ensai",
                        "Votre mot de passe vient d'être modifié.\n"
                        "Si vous n'êtes pas à l'origine de cette action, contactez-nous immédiatement.",
                    )
            except Exception as exc:
                print(f"Erreur lors du changement de mot de passe : {exc}")

        # --- E-mail de confirmation de modification de profil ---
        self._send_mail_notification(
            user_out.email,
            user_out.prenom,
            user_out.nom,
            "Votre profil a été mis à jour — BDE Ensai",
            "Les informations de votre profil ont été mises à jour avec succès.\n"
            "Si vous n'êtes pas à l'origine de cette action, veuillez nous contacter.",
        )

        return AccueilVue("Profil mis à jour — retour au menu principal")

    # =========================
    # Helpers validations et notifications
    # =========================
    def _send_mail_notification(self, to_email: str, prenom: str, nom: str, subject: str, message_body: str):
        """Envoi d’un e-mail de notification (best-effort)."""
        try:
            message_text = f"Bonjour {prenom} {nom},\n\n{message_body}\n\n— L’équipe du BDE Ensai"
            status, response = send_email_brevo(
                to_email=to_email,
                subject=subject,
                message_text=message_text,
            )
            if 200 <= status < 300:
                print(f"E-mail envoyé : {subject}")
            else:
                print(f"E-mail non envoyé (HTTP {status}).")
        except Exception as e:
            print(f"Erreur envoi e-mail : {e}")

    def _verifs_preliminaires_modif(self, nom: str, prenom: str, telephone: Optional[str], email: str) -> List[str]:
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
