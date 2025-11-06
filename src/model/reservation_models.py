from datetime import datetime
from pydantic import BaseModel, Field


class ReservationModelIn(BaseModel):
    """
    Modèle d'entrée pour la création d'une réservation.
    fk_utilisateur et fk_evenement sont obligatoires.
    """
    fk_utilisateur: int
    fk_evenement: int
    bus_aller: bool = False
    bus_retour: bool = False
    adherent: bool = False
    sam: bool = False
    boisson: bool = False


class ReservationModelOut(BaseModel):
    """
    Modèle de sortie pour la lecture d'une réservation.
    """
    id_reservation: int
    fk_utilisateur: int
    fk_evenement: int
    bus_aller: bool
    bus_retour: bool
    adherent: bool
    sam: bool
    boisson: bool
    date_reservation: datetime = Field(..., description="Horodatage automatique de la réservation")
