# view/evenement/modifier_evenement_vue.py
from __future__ import annotations
from typing import Optional
from datetime import date
import logging

from InquirerPy import inquirer
from pydantic import ValidationError

from view.vue_abstraite import VueAbstraite
from view.accueil.accueil_vue import AccueilVue
from view.session import Session

# ✅ Nouveau : import du service
from service.evenement_service import EvenementService
from model.evenement_models import EvenementModelOut

logger = logging.getLogger(__name__)

STATUTS = [
    "pas encore finalisé",
    "disponible en ligne",
    "déjà réalisé",
    "annulé",
]


class ModifierEvenementVue(VueAbstraite):
    """
    Vue de modification d'un événement (réservée aux administrateurs).
    Utilise EvenementService au lieu de EvenementDao.
    """

    def __init__(self) -> None:
        super().__init__("Modification d’un événement")
        self.service = EvenementService()  # ✅ Remplace le DAO

    # ---------- WRAPPERS : autorisent l'appel sur la classe ----------

    @classmethod
    def afficher(cls) -> None:
        """Permet d'appeler ModifierEvenementVue.afficher() sans instance."""
        return cls()._afficher_impl()

    @classmethod
    def choisir_menu(cls) -> Optional[AccueilVue]:
        """Permet d'appeler ModifierEvenementVue.choisir_menu() sans instance."""
        return cls()._choisir_menu_impl()

    # ---------- Implémentations réelles (instance) ----------

    def _afficher_impl(self) -> None:
        """
        Affiche l’en-tête de la vue de modification d’un événement.
        """
        print("\n" + "-" * 50)
        print("Modification d’un événement".center(50))
        print("-" * 50)

    def _choisir_menu_impl(self) -> Optional[AccueilVue]:
        """
        Gère la modification d’un événement.
        """
        sess = Session()
        user = sess.utilisateur
        if not sess.est_connecte() or not getattr(user, "administrateur", False):
            print("⛔ Accès refusé : vous devez être administrateur.")
            return AccueilVue("Accès refusé")

        # --- Sélection de l'événement à modifier ---
        try:
            id_str = inquirer.text(
                message="ID de l'événement à modifier :",
                validate=lambda t: t.isdigit() or "Entrez un entier",
            ).execute()
            id_evenement = int(id_str)
        except Exception as e:
            logger.exception("Erreur saisie ID: %s", e)
            print("⚠️ ID invalide.")
            return AccueilVue("Modification annulée — retour au menu principal")

        try:
            evt = self.service.get_event_by_id(id_evenement)
        except Exception as e:
            logger.exception("Erreur récupération événement: %s", e)
            print("❌ Erreur technique lors de la recherche.")
            return AccueilVue("Erreur technique — retour au menu principal")

        if evt is None:
            print(f"Aucun événement trouvé pour id={id_evenement}.")
            return AccueilVue("Introuvable — retour au menu principal")

        # --- Récapitulatif avant modification ---
        print("\nÉvénement courant :")
        print(f"  - Titre        : {evt.titre}")
        print(f"  - Date         : {evt.date_evenement}")
        print(f"  - Adresse      : {evt.adresse or '—'}")
        print(f"  - Ville        : {evt.ville or '—'}")
        print(f"  - Description  : {'—' if not evt.description else '(existe)'}")
        print(f"  - Capacité     : {evt.capacite}")
        print(f"  - Catégorie    : {evt.categorie or '—'}")
        print(f"  - Statut       : {evt.statut}")
        print(f"  - Utilisateur  : {evt.fk_utilisateur or 'NULL'}")
        print(f"  - Créé le      : {evt.date_creation}")

        # --- Saisie des nouvelles valeurs ---
        try:
            titre = inquirer.text(
                message=f"Titre (actuel: {evt.titre}) — vide=conserver :",
                default="",
            ).execute().strip()
            if titre == "":
                titre = evt.titre

            adresse_in = inquirer.text(
                message=f"Adresse (actuelle: {evt.adresse or '—'}) — vide=conserver, '-'=effacer :",
                default="",
            ).execute().strip()
            adresse = _clean_optional_text(adresse_in, evt.adresse)

            ville_in = inquirer.text(
                message=f"Ville (actuelle: {evt.ville or '—'}) — vide=conserver, '-'=effacer :",
                default="",
            ).execute().strip()
            ville = _clean_optional_text(ville_in, evt.ville)

            date_prompt = f"Date (YYYY-MM-DD) (actuelle: {evt.date_evenement}) — vide=conserver :"
            date_str = inquirer.text(
                message=date_prompt,
                validate=lambda t: (t == "" or _valid_date(t)) or "Format attendu YYYY-MM-DD",
                default="",
            ).execute()
            date_evenement = evt.date_evenement if date_str == "" else date.fromisoformat(date_str)

            description_in = inquirer.text(
                message=f"Description (actuelle: {'—' if not evt.description else '(existe)'}) — vide=conserver, '-'=effacer :",
                default="",
            ).execute().strip()
            description = _clean_optional_text(description_in, evt.description)

            capacite_str = inquirer.text(
                message=f"Capacité (actuelle: {evt.capacite}) — vide=conserver :",
                validate=lambda t: (t == "" or (t.isdigit() and int(t) > 0)) or "Entrez un entier > 0",
                default="",
            ).execute()
            capacite = evt.capacite if capacite_str == "" else int(capacite_str)

            categorie_in = inquirer.text(
                message=f"Catégorie (actuelle: {evt.categorie or '—'}) — vide=conserver, '-'=effacer :",
                default="",
            ).execute().strip()
            categorie = _clean_optional_text(categorie_in, evt.categorie)

            statut = inquirer.select(
                message="Statut :",
                choices=STATUTS,
                default=evt.statut if evt.statut in STATUTS else "pas encore finalisé",
            ).execute()

            fk_utilisateur_str = inquirer.text(
                message=f"ID utilisateur (actuel: {evt.fk_utilisateur or 'NULL'}) — vide=conserver, '-'=NULL :",
                validate=lambda t: (t in ('', '-') or t.isdigit()) or "Entrez un entier, vide, ou '-'",
                default="",
            ).execute()
            if fk_utilisateur_str == "":
                fk_utilisateur = evt.fk_utilisateur
            elif fk_utilisateur_str == "-":
                fk_utilisateur = None
            else:
                fk_utilisateur = int(fk_utilisateur_str)

            # Construction du modèle mis à jour
            evt_out = EvenementModelOut(
                id_evenement=evt.id_evenement,
                fk_utilisateur=fk_utilisateur,
                titre=titre,
                adresse=adresse,
                ville=ville,
                date_evenement=date_evenement,
                description=description,
                capacite=capacite,
                categorie=categorie,
                statut=statut,
                date_creation=evt.date_creation,
            )

        except ValidationError as ve:
            print("⚠️ Données invalides :")
            for err in ve.errors():
                loc = ".".join(str(x) for x in err.get("loc", []))
                msg = err.get("msg", "erreur")
                print(f"   - {loc}: {msg}")
            logger.info("ValidationError modification événement", exc_info=ve)
            return AccueilVue("Modification annulée — retour au menu principal")
        except Exception as e:
            logger.exception("Erreur de saisie: %s", e)
            print("⚠️ Erreur de saisie.")
            return AccueilVue("Modification annulée — retour au menu principal")

        # --- Appel du service pour mise à jour ---
        try:
            updated = self.service.update_event(evt_out)
        except Exception as e:
            logger.exception("Erreur update événement: %s", e)
            print("❌ Erreur lors de la mise à jour en base (contrainte ?).")
            return AccueilVue("Échec modification — retour au menu principal")

        if updated is None:
            print("Aucune ligne modifiée (événement introuvable ?).")
            return AccueilVue("Échec modification — retour au menu principal")

        print(f"✅ Événement mis à jour (id={updated.id_evenement}) : {updated.titre} — date {updated.date_evenement}")
        return AccueilVue("Événement modifié — retour au menu principal")


# ---------- Helpers ----------

def _valid_date(s: str) -> bool:
    """
    Vérifie si la chaîne donnée correspond à une date ISO valide.
    """
    try:
        date.fromisoformat(s)
        return True
    except Exception:
        return False


def _clean_optional_text(user_input: str, current_value: Optional[str]) -> Optional[str]:
    """
    Nettoie une saisie texte optionnelle en gérant la conservation ou la suppression de valeur
    Interprétation pour champs optionnels :
      - ''     -> conserver la valeur actuelle
      - '-'    -> None (effacer)
      - autre  -> nouvelle valeur strip()
    """
    if user_input == "":
        return current_value
    if user_input == "-":
        return None
    return user_input.strip()
