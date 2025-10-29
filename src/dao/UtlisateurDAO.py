# dao/utilisateur_dao.py
from typing import List, Optional
from datetime import datetime
import bcrypt

from dao.connection_manager import ConnectionManager
from models.utilisateur_models import UtilisateurModelIn, UtilisateurModelOut


class UtilisateurDao:
    """
    DAO pour la gestion des utilisateurs.
    Table supposée : 'utilisateur' avec au minimum :
      id_utilisateur (PK), email (unique), prenom, nom, numero_tel,
      mot_de_passe (hash bcrypt), date_creation, type (optionnel : 'USER' par défaut).
    """

    # ---------- Helpers mot de passe ----------
    @staticmethod
    def _hash_password(plain: str) -> str:
        if isinstance(plain, str):
            plain = plain.encode("utf-8")
        return bcrypt.hashpw(plain, bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def _check_password(plain: str, hashed: str) -> bool:
        if isinstance(plain, str):
            plain = plain.encode("utf-8")
        if isinstance(hashed, str):
            hashed = hashed.encode("utf-8")
        return bcrypt.checkpw(plain, hashed)

    # ---------- READ ----------
    def find_all(self, limit: int = 100, offset: int = 0) -> List[UtilisateurModelOut]:
        """
        Récupère une liste paginée d'utilisateurs.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, type, date_creation "
            "FROM utilisateur "
            "ORDER BY id_utilisateur "
            f"LIMIT {max(limit,0)} OFFSET {max(offset,0)}"
        )
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query)
                results = curs.fetchall()

        users: List[UtilisateurModelOut] = []
        for r in results:
            users.append(
                UtilisateurModelOut(
                    id_utilisateur=r["id_utilisateur"],
                    email=r["email"],
                    prenom=r["prenom"],
                    nom=r["nom"],
                    numero_tel=r["numero_tel"],
                    type=r.get("type", "USER"),
                    date_creation=r["date_creation"],
                )
            )
        return users

    def find_by_id(self, id_utilisateur: int) -> Optional[UtilisateurModelOut]:
        """
        Récupère un utilisateur par son ID.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, type, date_creation "
            "FROM utilisateur "
            "WHERE id_utilisateur = %(id)s"
        )
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_utilisateur})
                r = curs.fetchone()

        if r is None:
            return None

        return UtilisateurModelOut(
            id_utilisateur=r["id_utilisateur"],
            email=r["email"],
            prenom=r["prenom"],
            nom=r["nom"],
            numero_tel=r["numero_tel"],
            type=r.get("type", "USER"),
            date_creation=r["date_creation"],
        )

    def find_by_email(self, email: str) -> Optional[UtilisateurModelOut]:
        """
        Récupère un utilisateur par son email.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, type, date_creation "
            "FROM utilisateur "
            "WHERE email = %(email)s"
        )
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"email": email})
                r = curs.fetchone()

        if r is None:
            return None

        return UtilisateurModelOut(
            id_utilisateur=r["id_utilisateur"],
            email=r["email"],
            prenom=r["prenom"],
            nom=r["nom"],
            numero_tel=r["numero_tel"],
            type=r.get("type", "USER"),
            date_creation=r["date_creation"],
        )

    # ---------- CREATE ----------
    def create(self, user_in: UtilisateurModelIn) -> UtilisateurModelOut:
        """
        Crée un nouvel utilisateur (hash le mot de passe).
        """
        query = (
            "INSERT INTO utilisateur (email, prenom, nom, numero_tel, mot_de_passe, type, date_creation) "
            "VALUES (%(email)s, %(prenom)s, %(nom)s, %(numero_tel)s, %(mot_de_passe)s, %(type)s, %(date_creation)s) "
            "RETURNING id_utilisateur"
        )
        now = datetime.now()
        params = {
            "email": user_in.email,
            "prenom": user_in.prenom,
            "nom": user_in.nom,
            "numero_tel": user_in.numero_tel,
            "mot_de_passe": self._hash_password(user_in.mot_de_passe),
            "type": getattr(user_in, "type", "USER"),
            "date_creation": now,
        }

        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                new_id = curs.fetchone()["id_utilisateur"]

        return UtilisateurModelOut(
            id_utilisateur=new_id,
            email=user_in.email,
            prenom=user_in.prenom,
            nom=user_in.nom,
            numero_tel=user_in.numero_tel,
            type=params["type"],
            date_creation=now,
        )

    # ---------- UPDATE ----------
    def update(self, user_out: UtilisateurModelOut) -> Optional[UtilisateurModelOut]:
        """
        Met à jour un utilisateur (hors mot de passe).
        """
        query = (
            "WITH updated AS ("
            "  UPDATE utilisateur SET "
            "    email = %(email)s, "
            "    prenom = %(prenom)s, "
            "    nom = %(nom)s, "
            "    numero_tel = %(numero_tel)s, "
            "    type = %(type)s "
            "  WHERE id_utilisateur = %(id)s "
            "  RETURNING *"
            ") "
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, type, date_creation "
            "FROM updated"
        )
        params = {
            "id": user_out.id_utilisateur,
            "email": user_out.email,
            "prenom": user_out.prenom,
            "nom": user_out.nom,
            "numero_tel": user_out.numero_tel,
            "type": getattr(user_out, "type", "USER"),
        }

        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                r = curs.fetchone()

        if r is None:
            return None

        return UtilisateurModelOut(
            id_utilisateur=r["id_utilisateur"],
            email=r["email"],
            prenom=r["prenom"],
            nom=r["nom"],
            numero_tel=r["numero_tel"],
            type=r.get("type", "USER"),
            date_creation=r["date_creation"],
        )

    # ---------- DELETE ----------
    def delete(self, id_utilisateur: int) -> bool:
        """
        Supprime un utilisateur par ID.
        """
        query = "DELETE FROM utilisateur WHERE id_utilisateur = %(id)s"
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_utilisateur})
                return curs.rowcount > 0

    # ---------- AUTH ----------
    def authenticate(self, email: str, mot_de_passe: str) -> Optional[UtilisateurModelOut]:
        """
        Vérifie email/mot de passe et retourne l'utilisateur si OK.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, mot_de_passe, type, date_creation "
            "FROM utilisateur "
            "WHERE email = %(email)s"
        )
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"email": email})
                r = curs.fetchone()

        if r is None:
            return None

        if not self._check_password(mot_de_passe, r["mot_de_passe"]):
            return None

        return UtilisateurModelOut(
            id_utilisateur=r["id_utilisateur"],
            email=r["email"],
            prenom=r["prenom"],
            nom=r["nom"],
            numero_tel=r["numero_tel"],
            type=r.get("type", "USER"),
            date_creation=r["date_creation"],
        )

    def change_password(self, id_utilisateur: int, new_password: str) -> bool:
        """
        Met à jour le mot de passe (hash bcrypt).
        """
        query = (
            "UPDATE utilisateur SET mot_de_passe = %(pwd)s "
            "WHERE id_utilisateur = %(id)s"
        )
        params = {"pwd": self._hash_password(new_password), "id": id_utilisateur}
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                return curs.rowcount > 0
