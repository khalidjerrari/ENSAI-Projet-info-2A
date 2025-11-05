# dao/utilisateur_dao.py
from typing import List, Optional
import bcrypt

from dao.db_connection import DBConnection
from model.utilisateur_models import UtilisateurModelIn, UtilisateurModelOut


class UtilisateurDao:
    """
    DAO pour la gestion des utilisateurs.
    Table 'utilisateur' (schéma fourni) :
      id_utilisateur SERIAL PK
      nom, prenom, telephone, email (UNIQUE)
      mot_de_passe (hash), administrateur BOOLEAN, date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            "SELECT id_utilisateur, email, prenom, nom, telephone, administrateur, date_creation "
            "FROM utilisateur "
            "ORDER BY id_utilisateur "
            "LIMIT %(limit)s OFFSET %(offset)s"
        )
        params = {"limit": max(limit, 0), "offset": max(offset, 0)}

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                results = curs.fetchall()

        users: List[UtilisateurModelOut] = []
        for r in results:
            users.append(
                UtilisateurModelOut(
                    id_utilisateur=r["id_utilisateur"],
                    email=r["email"],
                    prenom=r["prenom"],
                    nom=r["nom"],
                    telephone=r["telephone"],
                    administrateur=r["administrateur"],
                    date_creation=r["date_creation"],
                )
            )
        return users

    def find_by_id(self, id_utilisateur: int) -> Optional[UtilisateurModelOut]:
        """
        Récupère un utilisateur par son ID.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, telephone, administrateur, date_creation "
            "FROM utilisateur "
            "WHERE id_utilisateur = %(id)s"
        )
        with DBConnection().getConnexion() as con:
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
            telephone=r["telephone"],
            administrateur=r["administrateur"],
            date_creation=r["date_creation"],
        )

    def find_by_email(self, email: str) -> Optional[UtilisateurModelOut]:
        """
        Récupère un utilisateur par son email.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, telephone, administrateur, date_creation "
            "FROM utilisateur "
            "WHERE email = %(email)s"
        )
        with DBConnection().getConnexion() as con:
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
            telephone=r["telephone"],
            administrateur=r["administrateur"],
            date_creation=r["date_creation"],
        )

    # ---------- CREATE ----------
    def create(self, user_in: UtilisateurModelIn) -> UtilisateurModelOut:
        """
        Crée un nouvel utilisateur (hash le mot de passe).
        Laisse la BDD remplir date_creation (DEFAULT CURRENT_TIMESTAMP).
        """
        query = (
            "INSERT INTO utilisateur (email, prenom, nom, telephone, mot_de_passe, administrateur) "
            "VALUES (%(email)s, %(prenom)s, %(nom)s, %(telephone)s, %(mot_de_passe)s, %(administrateur)s) "
            "RETURNING id_utilisateur, date_creation"
        )
        params = {
            "email": user_in.email,
            "prenom": user_in.prenom,
            "nom": user_in.nom,
            "telephone": user_in.telephone,
            "mot_de_passe": self._hash_password(user_in.mot_de_passe),
            "administrateur": getattr(user_in, "administrateur", False),
        }

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                row = curs.fetchone()

        return UtilisateurModelOut(
            id_utilisateur=row["id_utilisateur"],
            email=user_in.email,
            prenom=user_in.prenom,
            nom=user_in.nom,
            telephone=user_in.telephone,
            administrateur=params["administrateur"],
            date_creation=row["date_creation"],
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
            "    telephone = %(telephone)s, "
            "    administrateur = %(administrateur)s "
            "  WHERE id_utilisateur = %(id)s "
            "  RETURNING id_utilisateur, email, prenom, nom, telephone, administrateur, date_creation"
            ") "
            "SELECT * FROM updated"
        )
        params = {
            "id": user_out.id_utilisateur,
            "email": user_out.email,
            "prenom": user_out.prenom,
            "nom": user_out.nom,
            "telephone": user_out.telephone,
            "administrateur": getattr(user_out, "administrateur", False),
        }

        with DBConnection().getConnexion() as con:
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
            telephone=r["telephone"],
            administrateur=r["administrateur"],
            date_creation=r["date_creation"],
        )

    # ---------- DELETE ----------
    def delete(self, id_utilisateur: int) -> bool:
        """
        Supprime un utilisateur par ID.
        """
        query = "DELETE FROM utilisateur WHERE id_utilisateur = %(id)s"
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_utilisateur})
                return curs.rowcount > 0

    # ---------- AUTH ----------
    def authenticate(self, email: str, mot_de_passe: str) -> Optional[UtilisateurModelOut]:
        """
        Vérifie email/mot de passe et retourne l'utilisateur si OK.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, telephone, mot_de_passe, administrateur, date_creation "
            "FROM utilisateur "
            "WHERE email = %(email)s"
        )
        with DBConnection().getConnexion() as con:
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
            telephone=r["telephone"],
            administrateur=r["administrateur"],
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
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                return curs.rowcount > 0
