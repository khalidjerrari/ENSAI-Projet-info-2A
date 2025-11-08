# src/service/evenement_service.py
from typing import List, Optional
from dao.evenement_dao import EvenementDao
from model.evenement_models import EvenementModelIn, EvenementModelOut


class EvenementService:
    """
    Service pour la gestion des événements.
    Contient la logique métier au-dessus du DAO.
    """

    def __init__(self):
        self.dao = EvenementDao()

    # ---------- READ ----------
    def get_all_events(self, limit: int = 100, offset: int = 0) -> List[EvenementModelOut]:
        """Récupère tous les événements (paginés)."""
        return self.dao.find_all(limit=limit, offset=offset)

    def get_event_by_id(self, id_evenement: int) -> EvenementModelOut:
        """Récupère un événement par son ID, ou lève une erreur s’il n’existe pas."""
        event = self.dao.find_by_id(id_evenement)
        if not event:
            raise ValueError(f"Aucun événement trouvé avec l'id {id_evenement}.")
        return event

    def list_events_with_places(self, limit: int = 100, a_partir_du=None):
        """
        Liste les événements avec leurs places restantes (vue utilisée par ReservationVue).
        """
        return self.dao.lister_avec_places_restantes(limit=limit, a_partir_du=a_partir_du)

    def list_all_events(self, limit: int = 100):
        """
        Liste tous les événements (vue utilisée par StatistiquesInscriptionsVue).
        """
        return self.dao.lister_tous(limit=limit)

    # ---------- CREATE ----------
    def create_event(self, evenement_in: EvenementModelIn) -> EvenementModelOut:
        """Crée un nouvel événement, avec validation minimale."""
        if not evenement_in.titre or evenement_in.titre.strip() == "":
            raise ValueError("Le titre de l'événement est obligatoire.")
        if not evenement_in.date_evenement:
            raise ValueError("La date de l'événement est obligatoire.")
        if evenement_in.capacite is not None and evenement_in.capacite <= 0:
            raise ValueError("La capacité doit être un entier positif.")

        return self.dao.create(evenement_in)

    # ---------- UPDATE ----------
    def update_event(self, evenement_out: EvenementModelOut) -> EvenementModelOut:
        """Met à jour un événement existant."""
        existing = self.dao.find_by_id(evenement_out.id_evenement)
        if not existing:
            raise ValueError("Impossible de mettre à jour : événement introuvable.")

        updated = self.dao.update(evenement_out)
        if not updated:
            raise ValueError("Erreur lors de la mise à jour de l'événement.")
        return updated

    # ---------- DELETE ----------
    def delete_event(self, id_evenement: int) -> bool:
        """Supprime un événement existant."""
        existing = self.dao.find_by_id(id_evenement)
        if not existing:
            raise ValueError("Impossible de supprimer : événement introuvable.")
        return self.dao.delete(id_evenement)
