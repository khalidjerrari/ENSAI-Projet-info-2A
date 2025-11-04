from datetime import date, datetime
from pydantic import BaseModel, constr
from typing import Optional


class EvenementModelIn(BaseModel):
    fk_transport: int
    fk_utilisateur: Optional[int] = None
    titre: constr(max_length=150)
    adresse: Optional[constr(max_length=255)] = None
    ville: Optional[constr(max_length=100)] = None
    date_evenement: date
    description: Optional[str] = None
    capacite: int
    categorie: Optional[constr(max_length=50)] = None
    statut: Optional[str] = "pas encore finalisé"


class EvenementModelOut(BaseModel):
    id_evenement: int
    fk_transport: int
    fk_utilisateur: Optional[int] = None
    titre: str
    adresse: Optional[str] = None
    ville: Optional[str] = None
    date_evenement: date
    description: Optional[str] = None
    capacite: int
    categorie: Optional[str] = None
    statut: str
    date_creation: datetime
