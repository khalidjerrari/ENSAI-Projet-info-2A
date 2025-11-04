from datetime import datetime
from pydantic import BaseModel


class ReservationModelIn(BaseModel):
    fk_utilisateur: int
    fk_transport: int
    adherent: bool = False
    sam: bool = False
    boisson: bool = False


class ReservationModelOut(BaseModel):
    id_reservation: int
    fk_utilisateur: int
    fk_transport: int
    adherent: bool
    sam: bool
    boisson: bool
    date_reservation: datetime
