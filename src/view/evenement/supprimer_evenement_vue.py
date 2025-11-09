# view/evenement/supprimer_evenement_vue.py
from __future__ import annotations
from typing import Optional
import logging

from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.accueil.accueil_vue import AccueilVue
from view.session import Session

# On passe par le service
from service.evenement_service import EvenementService

logger = logging.getLogger(__name__)


class SupprimerEvenementVue(VueAbstraite):
    """
    Vue de suppression d'un événement (réservée aux administrateurs).

    Adaptée au nouveau schéma :
      - Suppression de toute référence à `fk_transport`
      - Utilise EvenementService au lieu du DAO direct
    """

    def __init__(self) -> None:
        super().__init__("Suppression d’un événement")
        self.service = EvenementService()

    # ---------- WRAPPERS : autorisent l'appel sur la classe ----------

    @classmethod
    def afficher(cls) -> None:
        """Permet d'appeler SupprimerEvenementVue.afficher() sans instance."""
        return cls()._afficher_impl()

    @classmethod
    def choisir_menu(cls) -> Optional[AccueilVue]:
        """Permet d'appeler SupprimerEvenementVue.choisir_menu() sans instance."""
        return cls()._choisir_menu_impl()

    # ---------- Implémentations réelles (instance) ----------

    def _afficher_impl(self) -> None:
        """
        Affiche l’en-tête de la vue de suppression d’un événement.
        """
        print("\n" + "-" * 50)
        print("Suppression d’un événement".center(50))
        print("-" * 50)

    def _choisir_menu_impl(self) -> Optional[AccueilVue]:
        """
        Gère la suppression d’un événement.
        """
        sess = Session()
        user = sess.utilisateur
        if not sess.est_connecte() or not getattr(user, "administrateur", False):
            print("⛔ Accès refusé : vous devez être administrateur.")
            return AccueilVue("Accès refusé")

        # --- Saisie de l'ID ---
        try:
            id_str = inquirer.text(
                message="ID de l'événement à supprimer :",
                validate=lambda t: t.isdigit() or "Entrez un entier",
            ).execute()
            id_evenement = int(id_str)
        except Exception as e:
            logger.exception("Erreur saisie ID: %s", e)
            print("⚠️ ID invalide.")
            return AccueilVue("Suppression annulée — retour au menu principal")

        # --- Récupération de l'événement (pour affichage/confirmation) ---
        try:
            evt = self.service.get_evenement_by_id(id_evenement)
        except Exception as e:
            logger.exception("Erreur lecture événement: %s", e)
            print("❌ Erreur lors de la récupération de l'événement.")
            return AccueilVue("Échec suppression — retour au menu principal")

        if evt is None:
            print(f"Aucun événement trouvé pour id={id_evenement}.")
            return AccueilVue("Introuvable — retour au menu principal")

        # --- Récapitulatif ---
        print("\nÉvénement ciblé :")
        print(f"  - ID           : {evt.id_evenement}")
        print(f"  - Titre        : {evt.titre}")
        print(f"  - Date         : {evt.date_evenement}")
        print(f"  - Ville        : {evt.ville or '—'}")
        print(f"  - Statut       : {evt.statut}")

        print("\n⚠️  Attention :")
        print("   - Toutes les réservations liées seront supprimées (ON DELETE CASCADE).")
        print("   - Les bus liés verront leur fk_evenement remis à NULL (ON DELETE SET NULL).")

        confirm = inquirer.confirm(
            message="Confirmez-vous la suppression ?",
            default=False,
        ).execute()

        if not confirm:
            print("Suppression annulée par l'utilisateur.")
            return AccueilVue("Suppression annulée — retour au menu principal")

        # --- Suppression via service ---
        try:
            ok = self.service.supprimer_evenement(id_evenement)
        except Exception as e:
            logger.exception("Erreur suppression événement: %s", e)
            print("❌ Erreur lors de la suppression en base.")
            return AccueilVue("Échec suppression — retour au menu principal")

        if not ok:
            print("Aucune ligne supprimée (événement introuvable ?).")
            return AccueilVue("Échec suppression — retour au menu principal")

        print(f"✅ Événement supprimé (id={id_evenement}).")
        return AccueilVue("Événement supprimé — retour au menu principal")
