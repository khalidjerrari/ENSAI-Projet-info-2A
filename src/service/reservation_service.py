# src/service/reservation_service.py
from typing import List, Optional
from dao.reservation_dao import ReservationDao
from model.reservation_models import ReservationModelIn, ReservationModelOut


class ReservationService:
    """
    Service pour la gestion des réservations.
    Contient la logique métier et la coordination avec le DAO.
    """

    def __init__(self):
        self.dao = ReservationDao()

    # ---------- READ ----------
    def get_reservations_by_user(self, id_utilisateur: int) -> List[ReservationModelOut]:
        """Récupère toutes les réservations d’un utilisateur."""
        return self.dao.find_by_user(id_utilisateur)

    def get_reservations_by_event(self, id_evenement: int) -> List[ReservationModelOut]:
        """Récupère toutes les réservations d’un événement."""
        return self.dao.find_by_event(id_evenement)

    def get_reservation_by_id(self, id_reservation: int) -> ReservationModelOut:
        """Récupère une réservation par son ID."""
        reservation = self.dao.find_by_id(id_reservation)
        if not reservation:
            raise ValueError(f"Aucune réservation trouvée avec l'id {id_reservation}.")
        return reservation

    # ---------- CREATE ----------
    def create_reservation(self, reservation_in: ReservationModelIn) -> ReservationModelOut:
        """
        Crée une nouvelle réservation.

        ✅ Règle métier :
        Un utilisateur ne peut pas réserver deux fois le même événement,
        mais peut réserver plusieurs événements différents.
        """
        # Vérifie s’il existe déjà une réservation pour cet utilisateur + cet événement
        existing_reservations = self.dao.find_by_user(reservation_in.fk_utilisateur)
        for r in existing_reservations:
            if r.fk_evenement == reservation_in.fk_evenement:
                raise ValueError("Vous avez déjà réservé une place pour cet événement.")

        # Si OK → création
        reservation = self.dao.create(reservation_in)
        if not reservation:
            raise ValueError("Échec de la création de la réservation (erreur base de données).")
        return reservation

    # ---------- UPDATE ----------
    def update_reservation_flags(
        self,
        id_reservation: int,
        *,
        bus_aller: Optional[bool] = None,
        bus_retour: Optional[bool] = None,
        adherent: Optional[bool] = None,
        sam: Optional[bool] = None,
        boisson: Optional[bool] = None,
    ) -> ReservationModelOut:
        """Met à jour les options (flags) d’une réservation existante."""
        existing = self.dao.find_by_id(id_reservation)
        if not existing:
            raise ValueError("Impossible de mettre à jour : réservation introuvable.")

        updated = self.dao.update_flags(
            id_reservation,
            bus_aller=bus_aller,
            bus_retour=bus_retour,
            adherent=adherent,
            sam=sam,
            boisson=boisson,
        )
        if not updated:
            raise ValueError("Erreur lors de la mise à jour de la réservation.")
        return updated

    # ---------- DELETE ----------
    def delete_reservation(self, id_reservation: int) -> bool:
        """Supprime une réservation existante."""
        existing = self.dao.find_by_id(id_reservation)
        if not existing:
            raise ValueError("Impossible de supprimer : réservation introuvable.")
        return self.dao.delete(id_reservation)

    # ---------- HELPERS / STATS ----------
    def count_reservations_for_event(self, id_evenement: int) -> int:
        """Compte le nombre de réservations pour un événement."""
        return self.dao.count_by_event(id_evenement)

    def user_has_reservation_for_event(self, id_utilisateur: int, id_evenement: int) -> bool:
        """Retourne True si l'utilisateur a déjà réservé ce même événement."""
        reservations = self.dao.find_by_user(id_utilisateur)
        return any(r.fk_evenement == id_evenement for r in reservations)
