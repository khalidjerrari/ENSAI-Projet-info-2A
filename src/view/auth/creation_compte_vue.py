# view/auth/creation_compte_vue.py
from typing import Optional, List
import re
import pwinput
from pydantic import ValidationError
from dotenv import load_dotenv

from view.session import Session
from service.utilisateur_service import UtilisateurService  # ✅ Nouveau import
from model.utilisateur_models import UtilisateurModelIn, UtilisateurModelOut
from utils.api_brevo import send_email_brevo

load_dotenv()


class CreationCompteVue:
    """
    Vue de création de compte (console).
    Utilise UtilisateurService pour la logique métier.
    """

    def __init__(self, message: str = ""):
        self.message = message
        self.service = UtilisateurService()  # ✅ on passe par le service

    def afficher(self) -> None:
        print("\n--- CRÉER UN COMPTE ---")
        if self.message:
            print(self.message)

    def choisir_menu(self) -> Optional["AccueilVue"]:
        from view.accueil.accueil_vue import AccueilVue

        # --- Saisie utilisateur ---
        nom = input("Nom : ").strip()
        prenom = input("Prénom : ").strip()
        telephone = input("Téléphone (optionnel) : ").strip() or None
        email = input("Email : ").strip()
        mot_de_passe = pwinput.pwinput(prompt="Mot de passe : ", mask="*")
        mot_de_passe2 = pwinput.pwinput(prompt="Confirmez le mot de passe : ", mask="*")

        # --- Vérifs préliminaires ---
        erreurs = self._verifs_preliminaires(
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            email=email,
            pwd=mot_de_passe,
            pwd2=mot_de_passe2,
        )
        if erreurs:
            print("\n Erreurs :")
            for e in erreurs:
                print(f" - {e}")
            return AccueilVue("Création annulée — retour au menu principal")

        # --- Création via Service ---
        try:
            user_in = UtilisateurModelIn(
                nom=nom,
                prenom=prenom,
                telephone=telephone,
                email=email,
                mot_de_passe=mot_de_passe,
                administrateur=False,
            )

            user_out: UtilisateurModelOut = self.service.create_user(user_in)  # ✅ Service
        except ValidationError as ve:
            print("\n Données invalides :")
            for err in ve.errors():
                loc = ".".join(str(x) for x in err.get("loc", []))
                msg = err.get("msg", "invalide")
                print(f" - {loc}: {msg}")
            return AccueilVue("Création annulée — retour au menu principal")
        except ValueError as e:
            print(f"❌ {e}")
            return AccueilVue("Création annulée — retour au menu principal")
        except Exception as e:
            print(f"⚠️ Erreur technique lors de la création du compte : {e}")
            return AccueilVue("Erreur technique — retour au menu principal")

        # --- Connexion automatique ---
        try:
            Session().connexion(user_out)
            print(f"✅ Compte créé et connecté : {user_out.prenom} {user_out.nom}")
        except Exception as exc:
            print(f"Compte créé mais échec de la connexion automatique : {exc}")

        # --- Envoi de l'e-mail de confirmation ---
        try:
            subject = "Confirmation de création de compte — BDE Ensai"
            message_text = (
                f"Bonjour {user_out.prenom} {user_out.nom},\n\n"
                "Votre compte a été créé avec succès.\n\n"
                "Vous pouvez désormais vous connecter et réserver vos événements.\n\n"
                "Si vous n'êtes pas à l'origine de cette action, veuillez nous contacter.\n\n"
                "— L’équipe du BDE Ensai"
            )
            status, _ = send_email_brevo(
                to_email=user_out.email,
                subject=subject,
                message_text=message_text,
            )
            if 200 <= status < 300:
                print("📧 Un e-mail de confirmation vous a été envoyé 🎉")
            else:
                print(f"⚠️ L'e-mail de confirmation n'a pas pu être envoyé (HTTP {status}).")
        except Exception as exc:
            print(f"Impossible d'envoyer l'e-mail de confirmation : {exc}")

        return AccueilVue("Compte créé — bienvenue !")

    # =========================
    # Helpers validations simples
    # =========================
    def _verifs_preliminaires(
        self,
        nom: str,
        prenom: str,
        telephone: Optional[str],
        email: str,
        pwd: str,
        pwd2: str,
    ) -> List[str]:
        erreurs: List[str] = []
        if not nom:
            erreurs.append("Le nom est obligatoire.")
        if not prenom:
            erreurs.append("Le prénom est obligatoire.")
        if pwd != pwd2:
            erreurs.append("Les mots de passe ne correspondent pas.")
        if not self._password_valide(pwd):
            erreurs.append("Mot de passe trop faible (min 8, avec lettre et chiffre).")
        if telephone and not self._telephone_valide(telephone):
            erreurs.append("Téléphone invalide (10 chiffres, ex. 0601020304).")
        if not self._email_rough_check(email):
            erreurs.append("Format d'email suspect.")
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
