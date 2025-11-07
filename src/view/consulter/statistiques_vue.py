from typing import Optional, Any, Dict, List
from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session

from dao.Consultation_evenementDAO import ConsultationEvenementDao
from dao.ReservationDAO import ReservationDao


class StatistiquesInscriptionsVue(VueAbstraite):
    """
    Vue admin (F05) : Statistiques globales sur les inscriptions.
    - Affiche un tableau agrégé par événement :
      * nombre d’inscrits
      * capacité totale
      * places restantes
      * taux d’occupation
      * nombre d’adhérents, SAM, payés, etc.
    """

    def __init__(self, message: str = ""):
        super().__init__(message)
        self.dao_evt = ConsultationEvenementDao()
        self.dao_resa = ReservationDao()

    # ----------------- Helpers -----------------
    @staticmethod
    def _is_admin() -> bool:
        user = Session().utilisateur
        return bool(user and getattr(user, "administrateur", False))

    def _load_all_events(self) -> List[Any]:
        """Charge tous les événements existants."""
        try:
            return self.dao_evt.lister_tous(limit=500)
        except Exception as exc:
            print(f"Erreur lors du chargement des événements : {exc}")
            return []

    def _load_reservations(self, id_evenement: int) -> List[Any]:
        """Récupère les réservations d’un événement donné."""
        try:
            return self.dao_resa.find_by_event(id_evenement)
        except Exception:
            return []

    def _compute_stats_event(self, reservations: List[Any], capacite: Optional[int]) -> Dict[str, int]:
        """Calcule les statistiques pour un événement."""
        inscrits = len(reservations)
        capacite_totale = capacite or 0
        restantes = max(0, capacite_totale - inscrits) if capacite_totale else None
        taux = (inscrits / capacite_totale * 100) if capacite_totale else 0

        return {
            "inscrits": inscrits,
            "capacite": capacite_totale,
            "restantes": restantes,
            "taux": round(taux, 1),
            "bus_aller": sum(1 for r in reservations if getattr(r, "bus_aller", False)),
            "bus_retour": sum(1 for r in reservations if getattr(r, "bus_retour", False)),
            "adherent": sum(1 for r in reservations if getattr(r, "adherent", False)),
            "sam": sum(1 for r in reservations if getattr(r, "sam", False)),
            "boisson": sum(1 for r in reservations if getattr(r, "boisson", False)),
            "paye": sum(1 for r in reservations if getattr(r, "paye", False)),
        }

    def _compute_stats_globale(self) -> List[Dict[str, Any]]:
        """Construit le tableau global de statistiques pour tous les événements."""
        evenements = self._load_all_events()
        tableau: List[Dict[str, Any]] = []

        for e in evenements:
            id_ev = getattr(e, "id_evenement", None)
            titre = getattr(e, "titre", "—")
            date_evt = getattr(e, "date_evenement", "—")
            capacite = getattr(e, "capacite", 0)

            reservations = self._load_reservations(id_ev)
            stats = self._compute_stats_event(reservations, capacite)
            tableau.append({
                "id_evenement": id_ev,
                "titre": titre,
                "date_evenement": date_evt,
                **stats,
            })
        return tableau

    def _print_stats_globale(self, tableau: List[Dict[str, Any]]):
        """Affiche le tableau récapitulatif global."""
        if not tableau:
            print("Aucun événement trouvé.")
            return

        print("\n--- 📊 Statistiques globales (tous les événements) ---")
        print(f"{'ID':>4} | {'Date':<10} | {'Titre':<25} | {'Cap.':>5} | {'Inscrits':>9} | {'Restantes':>10} | {'Occup.%':>8} | {'SAM':>4} | {'Adh.':>5} | {'Payés':>6}")
        print("-" * 95)

        total = {"capacite": 0, "inscrits": 0, "restantes": 0, "sam": 0, "adherent": 0, "paye": 0}
        for row in tableau:
            print(f"{row['id_evenement']:>4} | {str(row['date_evenement'])[:10]:<10} | {row['titre'][:25]:<25} | "
                  f"{row['capacite']:>5} | {row['inscrits']:>9} | {row['restantes']:>10} | "
                  f"{row['taux']:>8.1f} | {row['sam']:>4} | {row['adherent']:>5} | {row['paye']:>6}")
            for k in total.keys():
                total[k] += row.get(k, 0)

        taux_moyen = (total["inscrits"] / total["capacite"] * 100) if total["capacite"] else 0
        print("-" * 95)
        print(f"TOTAL | {'':<10} | {'':<25} | {total['capacite']:>5} | {total['inscrits']:>9} | {total['restantes']:>10} | "
              f"{taux_moyen:>8.1f} | {total['sam']:>4} | {total['adherent']:>5} | {total['paye']:>6}")

    # ----------------- Cycle Vue -----------------
    def afficher(self) -> None:
        super().afficher()

        if not self._is_admin():
            print("Accès refusé : réservé aux administrateurs.")
            return

        tableau = self._compute_stats_globale()
        self._print_stats_globale(tableau)

    def choisir_menu(self) -> Optional[VueAbstraite]:
        from view.administrateur.connexion_admin_vue import ConnexionAdminVue

        if not self._is_admin():
            return ConnexionAdminVue("Accès refusé.")

        action = inquirer.select(
            message="Actions statistiques :",
            choices=[
                "Actualiser les statistiques",
                "--- Retour ---",
            ],
        ).execute()

        if action == "Actualiser les statistiques":
            return StatistiquesInscriptionsVue()
        else:
            return ConnexionAdminVue("Retour au menu admin")
