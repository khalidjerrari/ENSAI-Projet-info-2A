# view/auth/creation_compte_vue.py
from typing import Optional, List
#from getpass import getpass
import re
import pwinput

from pydantic import ValidationError

from view.session import Session

from dao.UtilisateurDAO import UtilisateurDao
from model.utilisateur_models import (
    UtilisateurModelIn,
    UtilisateurModelOut,
)

from dotenv import load_dotenv
from utils.api_brevo import send_email_brevo
load_dotenv()


class CreationCompteVue:
    """
    Vue de création de compte (console).
    Utilise UtilisateurDao et les modèles Pydantic UtilisateurModelIn/Out.
    """

    def __init__(self, dao: Optional[UtilisateurDao] = None):
        self.dao = UtilisateurDao()

    def afficher(self) -> None:
        print("\n--- CRÉER UN COMPTE ---")

    def choisir_menu(self) -> Optional["AccueilVue"]:
        from view.accueil.accueil_vue import AccueilVue
        # --- Saisie ---
        nom = input("Nom : ").strip()
        prenom = input("Prénom : ").strip()
        telephone = input("Téléphone (optionnel) : ").strip() or None
        email = input("Email : ").strip()
        mot_de_passe = pwinput.pwinput(prompt="Mot de passe : ", mask="*")
        mot_de_passe2 = input("Confirmez le mot de passe : ")

        # --- Vérifs simples avant Pydantic ---
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

        # --- Unicité email ---
        try:
            if self.dao.find_by_email(email) is not None:
                print("Un compte existe déjà avec cet email.")
                return AccueilVue("Création annulée — retour au menu principal")
        except Exception as exc:
            print(f"Erreur technique lors de la vérification de l'email : {exc}")
            return AccueilVue("Erreur technique — retour au menu principal")

        # --- Validation Pydantic + Création via DAO ---
        try:
            user_in = UtilisateurModelIn(
                nom=nom,
                prenom=prenom,
                telephone=telephone,
                email=email,
                mot_de_passe=mot_de_passe,
                administrateur=False,
            )
        except ValidationError as ve:
            print("\n Données invalides :")
            for err in ve.errors():
                loc = ".".join(str(x) for x in err.get("loc", []))
                msg = err.get("msg", "invalide")
                print(f" - {loc}: {msg}")
            return AccueilVue("Création annulée — retour au menu principal")

        try:
            user_out: UtilisateurModelOut = self.dao.create(user_in)
        except Exception as exc:
            print(f"Erreur lors de la création du compte : {exc}")
            return AccueilVue("Création échouée — retour au menu principal")

        # --- Connexion automatique ---
        try:
            Session().connexion(user_out)
            print(f"Compte créé et connecté : {user_out.prenom} {user_out.nom}")
        except Exception as exc:
            print(f"Compte créé mais échec de la connexion automatique : {exc}")
        
        # --- ENVOI DE L'E-MAIL DE CONFIRMATION ---
        # AJOUT : import de l'envoi d'e-mail

        try:
            subject = "Confirmation de création de compte — BDE Ensai"
            message_text = (
                f"Bonjour {user_out.prenom} {user_out.nom},\n\n"
                "Votre compte a été créé avec succès.\n\n"
                "Vous pouvez désormais vous connecter et réserver vos événements.\n\n"
                "Si vous n'êtes pas à l'origine de cette action, veuillez nous contacter.\n\n"
                "— L’équipe du BDE Ensai"
            )
            status, response = send_email_brevo(
                to_email=user_out.email,
                subject=subject,
                message_text=message_text,
            )
            if status >= 200 and status < 300:
                print("Un e-mail de confirmation vous a été envoyé 🎉")
            else:
                print(f"Attention : l'e-mail de confirmation n'a pas pu être envoyé (HTTP {status}).")
        except Exception as exc:
            # On ne bloque pas la création si l'e-mail échoue
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
        # L'email sera validé par Pydantic (EmailStr) ; on garde un check léger pour feedback immédiat
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
