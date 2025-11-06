from datetime import date, datetime
from pydantic import BaseModel, constr, Field
from typing import Optional, Literal


class EvenementModelIn(BaseModel):
    """
    Modèle d'entrée pour la création d'un événement.
    fk_utilisateur peut être None (ON DELETE SET NULL).
    """
    fk_utilisateur: Optional[int] = None
    titre: constr(max_length=150)
    adresse: Optional[constr(max_length=100)] = None
    ville: Optional[constr(max_length=100)] = None
    date_evenement: date
    description: Optional[str] = None
    capacite: int = Field(..., gt=0)
    categorie: Optional[constr(max_length=50)] = None
    statut: Optional[
        Literal[
            "disponible en ligne",
            "déjà réalisé",
            "annulé",
            "pas encore finalisé"
        ]
    ] = "pas encore finalisé"


class EvenementModelOut(BaseModel):
    """
    Modèle de sortie pour la lecture d'un événement.
    """
    id_evenement: int
    fk_utilisateur: Optional[int] = None
    titre: str
    adresse: Optional[str] = None
    ville: Optional[str] = None
    date_evenement: date
    description: Optional[str] = None
    capacite: int
    categorie: Optional[str] = None
    statut: Literal[
        "disponible en ligne",
        "déjà réalisé",
        "annulé",
        "pas encore finalisé"
    ]
    date_creation: datetime
