from pydantic import BaseModel, constr
from datetime import date
from typing import Optional


class TransportModelIn(BaseModel):
    fk_bus: int
    ville_depart: constr(max_length=100)
    ville_arrivee: constr(max_length=100)
    date_transport: date


class TransportModelOut(BaseModel):
    id_transport: int
    fk_bus: int
    ville_depart: str
    ville_arrivee: str
    date_transport: date
