# dao/administrateur_dao.py
from typing import List, Optional
from datetime import datetime
import bcrypt

from dao.db_connection import DBConnection
from model.utilisateur_models import AdministrateurModelOut, AdministrateurModelIn


class AdministrateurDao:
    """
    DAO pour la gestion des administrateurs.
    Basé sur la table 'utilisateur' du schéma fourni :
      id_utilisateur SERIAL PK
      nom, prenom, telephone, email (UNIQUE), mot_de_passe (hash), administrateur BOOLEAN, date_creation TIMESTAMP
    Un administrateur est une ligne avec administrateur = TRUE.
    Les mots de passe sont stockés hashés (bcrypt).
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

    def find_all(self, limit: int = 100, offset: int = 0) -> List[AdministrateurModelOut]:
        """
        Récupère une liste paginée d'administrateurs.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, telephone, administrateur, date_creation "
            "FROM utilisateur "
            "WHERE administrateur = TRUE "
            "ORDER BY id_utilisateur "
            "LIMIT %(limit)s OFFSET %(offset)s"
        )
        params = {"limit": max(limit, 0), "offset": max(offset, 0)}

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                results = curs.fetchall()

        admins: List[AdministrateurModelOut] = []
        for res in results:
            admins.append(
                AdministrateurModelOut(
                    id_utilisateur=res["id_utilisateur"],
                    email=res["email"],
                    prenom=res["prenom"],
                    nom=res["nom"],
                    telephone=res["telephone"],
                    administrateur=res["administrateur"],
                    date_creation=res["date_creation"],
                )
            )
        return admins

    def find_by_id(self, id_utilisateur: int) -> Optional[AdministrateurModelOut]:
        """
        Récupère un administrateur par son ID.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, telephone, administrateur, date_creation "
            "FROM utilisateur "
            "WHERE id_utilisateur = %(id)s AND administrateur = TRUE"
        )
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_utilisateur})
                res = curs.fetchone()

        if res is None:
            return None

        return AdministrateurModelOut(
            id_utilisateur=res["id_utilisateur"],
            email=res["email"],
            prenom=res["prenom"],
            nom=res["nom"],
            telephone=res["telephone"],
            administrateur=res["administrateur"],
            date_creation=res["date_creation"],
        )

    def find_by_email(self, email: str) -> Optional[AdministrateurModelOut]:
        """
        Récupère un administrateur par email.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, telephone, administrateur, date_creation "
            "FROM utilisateur "
            "WHERE email = %(email)s AND administrateur = TRUE"
        )
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"email": email})
                res = curs.fetchone()

        if res is None:
            return None

        return AdministrateurModelOut(
            id_utilisateur=res["id_utilisateur"],
            email=res["email"],
            prenom=res["prenom"],
            nom=res["nom"],
            telephone=res["telephone"],
            administrateur=res["administrateur"],
            date_creation=res["date_creation"],
        )

    # ---------- CREATE ----------

    def create(self, admin_in: AdministrateurModelIn) -> AdministrateurModelOut:
        """
        Crée un nouvel administrateur (administrateur=TRUE).
        admin_in.mot_de_passe est hashé avant insertion.
        """
        query = (
            "INSERT INTO utilisateur (email, prenom, nom, telephone, mot_de_passe, administrateur) "
            "VALUES (%(email)s, %(prenom)s, %(nom)s, %(telephone)s, %(mot_de_passe)s, TRUE) "
            "RETURNING id_utilisateur, date_creation"
        )
        params = {
            "email": admin_in.email,
            "prenom": admin_in.prenom,
            "nom": admin_in.nom,
            "telephone": admin_in.telephone,
            "mot_de_passe": self._hash_password(admin_in.mot_de_passe),
        }

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                row = curs.fetchone()

        return AdministrateurModelOut(
            id_utilisateur=row["id_utilisateur"],
            email=admin_in.email,
            prenom=admin_in.prenom,
            nom=admin_in.nom,
            telephone=admin_in.telephone,
            administrateur=True,
            date_creation=row["date_creation"],
        )

    # ---------- UPDATE ----------

    def update(self, admin_out: AdministrateurModelOut) -> Optional[AdministrateurModelOut]:
        """
        Met à jour un administrateur (hors mot de passe).
        """
        query = (
            "WITH updated AS ( "
            " UPDATE utilisateur SET "
            "   email = %(email)s, "
            "   prenom = %(prenom)s, "
            "   nom = %(nom)s, "
            "   telephone = %(telephone)s "
            " WHERE id_utilisateur = %(id)s AND administrateur = TRUE "
            " RETURNING id_utilisateur, email, prenom, nom, telephone, administrateur, date_creation "
            ") "
            "SELECT * FROM updated"
        )
        params = {
            "id": admin_out.id_utilisateur,
            "email": admin_out.email,
            "prenom": admin_out.prenom,
            "nom": admin_out.nom,
            "telephone": admin_out.telephone,
        }

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                res = curs.fetchone()

        if res is None:
            return None

        return AdministrateurModelOut(
            id_utilisateur=res["id_utilisateur"],
            email=res["email"],
            prenom=res["prenom"],
            nom=res["nom"],
            telephone=res["telephone"],
            administrateur=res["administrateur"],
            date_creation=res["date_creation"],
        )

    # ---------- DELETE ----------

    def delete(self, id_utilisateur: int) -> bool:
        """
        Supprime un administrateur par ID.
        """
        query = "DELETE FROM utilisateur WHERE id_utilisateur = %(id)s AND administrateur = TRUE"
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_utilisateur})
                return curs.rowcount > 0

    # ---------- AUTH / SECURITY ----------

    def authenticate(self, email: str, mot_de_passe: str) -> Optional[AdministrateurModelOut]:
        """
        Vérifie les identifiants et retourne l'admin si OK, sinon None.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, telephone, mot_de_passe, administrateur, date_creation "
            "FROM utilisateur WHERE email = %(email)s AND administrateur = TRUE"
        )
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"email": email})
                res = curs.fetchone()

        if res is None:
            return None

        if not self._check_password(mot_de_passe, res["mot_de_passe"]):
            return None

        return AdministrateurModelOut(
            id_utilisateur=res["id_utilisateur"],
            email=res["email"],
            prenom=res["prenom"],
            nom=res["nom"],
            telephone=res["telephone"],
            administrateur=res["administrateur"],
            date_creation=res["date_creation"],
        )

    def change_password(self, id_utilisateur: int, new_password: str) -> bool:
        """
        Change le mot de passe d'un administrateur (hash bcrypt).
        """
        query = (
            "UPDATE utilisateur SET mot_de_passe = %(pwd)s "
            "WHERE id_utilisateur = %(id)s AND administrateur = TRUE"
        )
        params = {"pwd": self._hash_password(new_password), "id": id_utilisateur}

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                return curs.rowcount > 0
