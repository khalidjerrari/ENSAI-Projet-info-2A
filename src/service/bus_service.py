# service/bus_service.py
from typing import List, Optional
from dao.bus_dao import CreneauBusDao
from model.creneau_bus import CreneauBus


class CreneauBusService:
    """
    Service pour la gestion des créneaux de bus (table `bus`).
    Contient la logique métier et délègue les opérations au DAO.
    """

    def __init__(self):
        self.dao = CreneauBusDao()

    # ---------- CREATE ----------
    def create_bus(self, bus: CreneauBus) -> CreneauBus:
        """
        Crée un nouveau créneau de bus après vérifications métier.
        """
        if not bus.description or bus.description.strip() == "":
            raise ValueError("La description du bus est obligatoire.")
        if bus.nombre_places <= 0:
            raise ValueError("Le nombre de places doit être supérieur à zéro.")
        if self.dao.exists_description(bus.description):
            raise ValueError(f"Un bus avec la description '{bus.description}' existe déjà.")

        created = self.dao.create(bus)
        if not created:
            raise ValueError("Erreur lors de la création du bus.")
        return created

    # ---------- READ ----------
    def get_all_buses(self, limit: int = 100, offset: int = 0) -> List[CreneauBus]:
        """Retourne la liste paginée de tous les bus."""
        return self.dao.find_all(limit=limit, offset=offset)

    def get_bus_by_id(self, id_bus: int) -> CreneauBus:
        """Retourne un bus par son ID, ou lève une erreur si non trouvé."""
        bus = self.dao.find_by_id(id_bus)
        if not bus:
            raise ValueError(f"Aucun bus trouvé avec l'id {id_bus}.")
        return bus

    def get_buses_by_event(self, id_evenement: int) -> List[CreneauBus]:
        """Retourne tous les bus liés à un événement."""
        return self.dao.find_by_event(id_evenement)

    def get_bus_by_description(self, description: str) -> CreneauBus:
        """Retourne un bus par sa description."""
        bus = self.dao.find_by_description(description)
        if not bus:
            raise ValueError(f"Aucun bus trouvé avec la description '{description}'.")
        return bus

    # ---------- UPDATE ----------
    def update_bus(self, bus: CreneauBus) -> CreneauBus:
        """Met à jour un bus existant (tous champs)."""
        existing = self.dao.find_by_id(bus.id_bus)
        if not existing:
            raise ValueError("Impossible de mettre à jour : bus introuvable.")
        if bus.nombre_places <= 0:
            raise ValueError("Le nombre de places doit être supérieur à zéro.")
        if bus.description != existing.description and self.dao.exists_description(bus.description):
            raise ValueError(f"Un autre bus utilise déjà la description '{bus.description}'.")

        updated = self.dao.update(bus)
        if not updated:
            raise ValueError("Erreur lors de la mise à jour du bus.")
        return updated

    def update_places(self, id_bus: int, nombre_places: int) -> CreneauBus:
        """Met à jour uniquement le nombre de places."""
        if nombre_places <= 0:
            raise ValueError("Le nombre de places doit être supérieur à zéro.")
        existing = self.dao.find_by_id(id_bus)
        if not existing:
            raise ValueError("Bus introuvable pour mise à jour du nombre de places.")
        updated = self.dao.update_places(id_bus, nombre_places)
        if not updated:
            raise ValueError("Erreur lors de la mise à jour du nombre de places.")
        return updated

    # ---------- DELETE ----------
    def delete_bus(self, id_bus: int) -> bool:
        """Supprime un bus par son ID."""
        existing = self.dao.find_by_id(id_bus)
        if not existing:
            raise ValueError("Impossible de supprimer : bus introuvable.")
        return self.dao.delete(id_bus)

    # ---------- HELPERS ----------
    def count_buses_for_event(self, id_evenement: int) -> int:
        """Retourne le nombre de bus pour un événement donné."""
        return self.dao.count_for_event(id_evenement)
