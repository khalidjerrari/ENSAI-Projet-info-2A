from datetime import datetime
from pydantic import BaseModel, EmailStr, constr
from typing import Optional


# ---------- Modèles Utilisateur ----------

class UtilisateurModelIn(BaseModel):
    nom: constr(max_length=50)
    prenom: constr(max_length=100)
    telephone: Optional[constr(max_length=20)] = None
    email: EmailStr
    mot_de_passe: str
    administrateur: bool = False


class UtilisateurModelOut(BaseModel):
    id_utilisateur: int
    nom: str
    prenom: str
    telephone: Optional[str] = None
    email: EmailStr
    administrateur: bool
    date_creation: datetime


# ---------- Modèles Administrateur ----------

class AdministrateurModelIn(UtilisateurModelIn):
    administrateur: bool = True


class AdministrateurModelOut(UtilisateurModelOut):
    administrateur: bool = True
