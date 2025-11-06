from pydantic import BaseModel, constr, Field
from typing import Optional, Literal


class BusModelIn(BaseModel):
    """
    Modèle d'entrée pour la création d'un bus.
    fk_evenement peut être None si le bus n'est pas encore associé à un événement.
    """
    fk_evenement: Optional[int] = None
    matricule: Optional[constr(max_length=20)] = None
    nombre_places: int = Field(..., gt=0)
    direction: Literal["aller", "retour"] = "aller"
    description: constr(max_length=100)


class BusModelOut(BaseModel):
    """
    Modèle de sortie pour la lecture d'un bus.
    """
    id_bus: int
    fk_evenement: Optional[int] = None
    matricule: Optional[str] = None
    nombre_places: int
    direction: Literal["aller", "retour"]
    description: str
