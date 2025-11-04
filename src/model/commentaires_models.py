from datetime import datetime
from pydantic import BaseModel, conint
from typing import Optional


class CommentaireModelIn(BaseModel):
    fk_reservation: int
    fk_utilisateur: int
    note: conint(ge=1, le=5)
    avis: Optional[str] = None


class CommentaireModelOut(BaseModel):
    id_commentaire: int
    fk_reservation: int
    fk_utilisateur: int
    note: int
    avis: Optional[str] = None
    date_commentaire: datetime
