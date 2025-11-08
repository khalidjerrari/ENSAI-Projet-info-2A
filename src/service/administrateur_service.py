# service/administrateur_service.py
from typing import List, Optional

from dao.administrateur_dao import AdministrateurDao
from model.utilisateur_models import AdministrateurModelOut, AdministrateurModelIn


class AdministrateurService:
    """
    Service pour la gestion des administrateurs.
    Contient la logique métier, les validations et appelle le DAO.
    """

    def __init__(self):
        self.dao = AdministrateurDao()

    # ---------- READ ----------
    def get_all_admins(self, limit: int = 100, offset: int = 0) -> List[AdministrateurModelOut]:
        return self.dao.find_all(limit=limit, offset=offset)

    def get_admin_by_id(self, id_utilisateur: int) -> Optional[AdministrateurModelOut]:
        admin = self.dao.find_by_id(id_utilisateur)
        if not admin:
            raise ValueError(f"Aucun administrateur trouvé avec l'id {id_utilisateur}")
        return admin

    def get_admin_by_email(self, email: str) -> Optional[AdministrateurModelOut]:
        admin = self.dao.find_by_email(email)
        if not admin:
            raise ValueError(f"Aucun administrateur trouvé avec l'email {email}")
        return admin

    # ---------- CREATE ----------
    def create_admin(self, admin_in: AdministrateurModelIn) -> AdministrateurModelOut:
        # Vérifie si un utilisateur avec le même email existe déjà
        existing = self.dao.find_by_email(admin_in.email)
        if existing:
            raise ValueError(f"L'email '{admin_in.email}' est déjà utilisé par un administrateur.")

        return self.dao.create(admin_in)

    # ---------- UPDATE ----------
    def update_admin(self, admin_out: AdministrateurModelOut) -> AdministrateurModelOut:
        # Vérifie que l’administrateur existe avant de le mettre à jour
        existing = self.dao.find_by_id(admin_out.id_utilisateur)
        if not existing:
            raise ValueError("Impossible de mettre à jour : administrateur introuvable.")
        return self.dao.update(admin_out)

    # ---------- DELETE ----------
    def delete_admin(self, id_utilisateur: int) -> bool:
        existing = self.dao.find_by_id(id_utilisateur)
        if not existing:
            raise ValueError("Impossible de supprimer : administrateur introuvable.")
        return self.dao.delete(id_utilisateur)

    # ---------- AUTH ----------
    def authenticate_admin(self, email: str, mot_de_passe: str) -> Optional[AdministrateurModelOut]:
        admin = self.dao.authenticate(email, mot_de_passe)
        if not admin:
            raise ValueError("Email ou mot de passe incorrect.")
        return admin

    def change_admin_password(self, id_utilisateur: int, new_password: str) -> bool:
        existing = self.dao.find_by_id(id_utilisateur)
        if not existing:
            raise ValueError("Administrateur introuvable pour mise à jour du mot de passe.")
        return self.dao.change_password(id_utilisateur, new_password)
