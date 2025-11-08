# service/utilisateur_service.py
from typing import List, Optional

from dao.utilisateur_dao import UtilisateurDao
from model.utilisateur_models import UtilisateurModelIn, UtilisateurModelOut
from view.session import Session


class UtilisateurService:
    """
    Service pour la gestion des utilisateurs.
    Contient la logique métier au-dessus du DAO.
    """

    def __init__(self):
        self.dao = UtilisateurDao()

    # ---------- READ ----------
    def get_all_users(self, limit: int = 100, offset: int = 0) -> List[UtilisateurModelOut]:
        return self.dao.find_all(limit=limit, offset=offset)

    def get_user_by_id(self, id_utilisateur: int) -> Optional[UtilisateurModelOut]:
        user = self.dao.find_by_id(id_utilisateur)
        if not user:
            raise ValueError(f"Aucun utilisateur trouvé avec l'id {id_utilisateur}")
        return user

    def get_user_by_email(self, email: str) -> Optional[UtilisateurModelOut]:
        return self.dao.find_by_email(email)

    # ---------- CREATE ----------
    def create_user(self, user_in: UtilisateurModelIn) -> UtilisateurModelOut:
        # Vérifie si l’email existe déjà
        existing = self.dao.find_by_email(user_in.email)
        if existing:
            raise ValueError(f"L'email '{user_in.email}' est déjà utilisé.")

        return self.dao.create(user_in)

    # ---------- UPDATE ----------
    def update_user(self, user_out: UtilisateurModelOut) -> UtilisateurModelOut:
        if not self.dao.find_by_id(user_out.id_utilisateur):
            raise ValueError("Impossible de mettre à jour : utilisateur introuvable.")
        return self.dao.update(user_out)

    # ---------- DELETE ----------
    def delete_user(self, id_utilisateur: int) -> bool:
        if not self.dao.find_by_id(id_utilisateur):
            raise ValueError("Impossible de supprimer : utilisateur introuvable.")
        return self.dao.delete(id_utilisateur)

    # ---------- AUTH ----------
    def authenticate_user(self, email: str, password: str) -> Optional[UtilisateurModelOut]:
        user = self.dao.authenticate(email, password)
        if not user:
            raise ValueError("Email ou mot de passe incorrect.")
        return user

    def change_user_password(self, id_utilisateur: int, new_password: str) -> bool:
        if not self.dao.find_by_id(id_utilisateur):
            raise ValueError("Utilisateur introuvable pour mise à jour du mot de passe.")
        return self.dao.change_password(id_utilisateur, new_password)

    # ---------- SESSION ----------
    def deconnexion(self) -> bool:
        """Déconnecte l'utilisateur courant (vide la session)."""
        Session().deconnexion()
        return True

    def get_current_user(self) -> Optional[UtilisateurModelOut]:
        """Renvoie l'utilisateur actuellement connecté, ou None."""
        return Session().utilisateur
