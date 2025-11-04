from pydantic import BaseModel, constr
from typing import Optional


class BusModelIn(BaseModel):
    matricule: constr(max_length=50)
    nombre_places: int


class BusModelOut(BaseModel):
    id_bus: int
    matricule: str
    nombre_places: int
