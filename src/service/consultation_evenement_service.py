# service/consultation_evenement_service.py
from typing import List, Optional, Dict, Any
from datetime import date

from dao.consultation_evenement_dao import ConsultationEvenementDao
from model.evenement_models import EvenementModelOut


class ConsultationEvenementService:
    """
    Service de lecture seule pour la consultation des événements.
    Fournit une couche métier au-dessus du DAO pour filtrer, valider
    et présenter les données de manière sécurisée.
    """

    def __init__(self):
        self.dao = ConsultationEvenementDao()

    # ---------- LISTES SIMPLES ----------
    def lister_tous(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "date_evenement ASC, id_evenement ASC",
    ) -> List[EvenementModelOut]:
        """Liste paginée de tous les événements (triés)."""
        self._validate_order_by(order_by)
        return self.dao.lister_tous(limit=limit, offset=offset, order_by=order_by)

    def lister_disponibles(
        self,
        limit: int = 100,
        offset: int = 0,
        a_partir_du: Optional[date] = None,
    ) -> List[EvenementModelOut]:
        """Liste des événements disponibles (optionnellement à partir d'une date donnée)."""
        return self.dao.lister_disponibles(limit=limit, offset=offset, a_partir_du=a_partir_du)

    # ---------- RECHERCHE MULTI-FILTRES ----------
    def rechercher(
        self,
        ville: Optional[str] = None,
        categorie: Optional[str] = None,
        statut: Optional[str] = None,
        date_min: Optional[date] = None,
        date_max: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[EvenementModelOut]:
        """Recherche d'événements selon différents filtres facultatifs."""
        # Validation simple des bornes temporelles
        if date_min and date_max and date_min > date_max:
            raise ValueError("La date minimale ne peut pas être postérieure à la date maximale.")
        return self.dao.rechercher(
            ville=ville,
            categorie=categorie,
            statut=statut,
            date_min=date_min,
            date_max=date_max,
            limit=limit,
            offset=offset,
        )

    # ---------- LISTE AVEC PLACES RESTANTES ----------
    def lister_avec_places_restantes(
        self,
        limit: int = 100,
        offset: int = 0,
        seulement_disponibles: bool = True,
        a_partir_du: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Liste les événements en y ajoutant la capacité restante
        (calculée à partir du nombre de réservations).
        """
        return self.dao.lister_avec_places_restantes(
            limit=limit,
            offset=offset,
            seulement_disponibles=seulement_disponibles,
            a_partir_du=a_partir_du,
        )

    # ---------- VALIDATION INTERNE ----------
    def _validate_order_by(self, order_by: str) -> None:
        """Valide le champ de tri pour éviter les injections SQL."""
        champs_valides = {
            "id_evenement",
            "date_evenement",
            "ville",
            "categorie",
            "titre",
            "date_creation",
        }
        # On autorise uniquement les champs connus et ASC/DESC
        tokens = [t.strip().replace(",", "") for t in order_by.split()]
        for token in tokens:
            # Vérifie que les noms de colonnes appartiennent à la liste blanche
            if token.lower() not in {"asc", "desc"} and token not in champs_valides:
                raise ValueError(f"Champ de tri invalide : {token}")
