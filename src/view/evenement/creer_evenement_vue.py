# src/view/evenement/creer_evenement_vue.py
from __future__ import annotations
from typing import Optional
from datetime import date
import logging

from InquirerPy import inquirer
from pydantic import ValidationError

from view.vue_abstraite import VueAbstraite
from view.accueil.accueil_vue import AccueilVue
from view.session import Session

# ✅ Passage au service (plus de DAO direct)
from service.evenement_service import EvenementService
from model.evenement_models import EvenementModelIn

logger = logging.getLogger(__name__)

STATUTS = [
    "pas encore finalisé",
    "disponible en ligne",
    "déjà réalisé",
    "annulé",
]


class CreerEvenementVue(VueAbstraite):
    """
    Vue de création d'un événement (réservée aux administrateurs).
    Utilise EvenementService.
    """

    def __init__(self, message: str = "") -> None:
        super().__init__(message)
        self.service = EvenementService()

    def afficher(self) -> None:
        """
        Affiche l’en-tête de la vue de création d’un événement.
        """
        print("\n" + "-" * 50)
        print("Création d’un événement".center(50))
        print("-" * 50)
        if self.message:
            print(self.message)

    def choisir_menu(self) -> Optional[AccueilVue]:
        """
        Gère la création d'un événement
        """
        sess = Session()
        user = sess.utilisateur
        if not sess.est_connecte() or not getattr(user, "administrateur", False):
            print("⛔ Accès refusé : vous devez être administrateur.")
            return AccueilVue("Accès refusé")

        # --- Saisie des champs ---
        try:
            titre = inquirer.text(
                message="Titre :",
                validate=lambda t: len(t.strip()) > 0 or "Titre requis",
            ).execute().strip()

            adresse = inquirer.text(message="Adresse (optionnel) :").execute().strip() or None
            ville = inquirer.text(message="Ville (optionnel) :").execute().strip() or None

            date_str = inquirer.text(
                message="Date de l'événement (YYYY-MM-DD) :",
                validate=lambda t: (_valid_date(t) or "Format attendu YYYY-MM-DD"),
            ).execute()
            date_evenement = date.fromisoformat(date_str)

            description = inquirer.text(message="Description (optionnel) :").execute().strip() or None

            # ✅ Correction de la saisie de la capacité (plus de ValueError)
            while True:
                capacite_str = inquirer.text(
                    message="Capacité :",
                    validate=lambda t: (t.isdigit() and int(t) > 0) or "Entrez un entier > 0",
                ).execute().strip()

                if not capacite_str:
                    print("⚠️  La capacité est obligatoire.")
                    continue

                try:
                    capacite = int(capacite_str)
                    break
                except ValueError:
                    print("❌ Veuillez entrer un nombre entier valide.")

            categorie = inquirer.text(message="Catégorie (optionnel) :").execute().strip() or None

            statut = inquirer.select(
                message="Statut :",
                choices=STATUTS,
                default="pas encore finalisé",
            ).execute()

            fk_utilisateur = user.id_utilisateur

            # --- Construction du modèle d'entrée ---
            evt_in = EvenementModelIn(
                fk_utilisateur=fk_utilisateur,
                titre=titre,
                adresse=adresse,
                ville=ville,
                date_evenement=date_evenement,
                description=description,
                capacite=capacite,
                categorie=categorie,
                statut=statut,
            )

        except ValidationError as ve:
            print("❌ Données invalides :")
            for err in ve.errors():
                loc = ".".join(str(x) for x in err.get("loc", []))
                msg = err.get("msg", "erreur")
                print(f"   - {loc}: {msg}")
            logger.info("ValidationError création événement", exc_info=ve)
            return AccueilVue("Création annulée — retour au menu principal")

        except Exception as e:
            logger.exception("Erreur de saisie: %s", e)
            print("⚠️ Erreur de saisie.")
            return AccueilVue("Création annulée — retour au menu principal")

        # --- Appel au service (au lieu du DAO) ---
        try:
            evt_out = self.service.create_event(evt_in)
        except Exception as e:
            logger.exception("Erreur Service création événement: %s", e)
            print("❌ Erreur lors de la création en base (contrainte non respectée ?).")
            return AccueilVue("Échec création — retour au menu principal")

        print(f"✅ Événement créé (id={evt_out.id_evenement}) : {evt_out.titre} — le {evt_out.date_evenement}")
        return AccueilVue("Événement créé — retour au menu principal")


def _valid_date(s: str) -> bool:
    try:
        date.fromisoformat(s)
        return True
    except Exception:
        return False
