# dao/administrateur_dao.py
from typing import List, Optional
from datetime import datetime
import bcrypt

from dao.connection_manager import ConnectionManager
from models.utilisateur_models import AdministrateurModelOut, AdministrateurModelIn


class AdministrateurDao:
    """
    DAO pour la gestion des administrateurs dans la base de données.
    Stockage dans la table 'utilisateur' (ou 'utilisateurs') avec la colonne type='ADMIN'.
    Le mot de passe est stocké hashé (bcrypt).
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
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, niveau_acces, type, date_creation "
            "FROM utilisateur "
            "WHERE type = 'ADMIN' "
            "ORDER BY id_utilisateur "
            f"LIMIT {max(limit,0)} OFFSET {max(offset,0)}"
        )
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query)
                results = curs.fetchall()

        admins: List[AdministrateurModelOut] = []
        for res in results:
            admins.append(
                AdministrateurModelOut(
                    id_utilisateur=res["id_utilisateur"],
                    email=res["email"],
                    prenom=res["prenom"],
                    nom=res["nom"],
                    numero_tel=res["numero_tel"],
                    niveau_acces=res["niveau_acces"],
                    type=res["type"],
                    date_creation=res["date_creation"],
                )
            )
        return admins

    def find_by_id(self, id_utilisateur: int) -> Optional[AdministrateurModelOut]:
        """
        Récupère un administrateur par son ID.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, niveau_acces, type, date_creation "
            "FROM utilisateur "
            "WHERE id_utilisateur = %(id)s AND type = 'ADMIN'"
        )
        with ConnectionManager().getConnexion() as con:
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
            numero_tel=res["numero_tel"],
            niveau_acces=res["niveau_acces"],
            type=res["type"],
            date_creation=res["date_creation"],
        )

    def find_by_email(self, email: str) -> Optional[AdministrateurModelOut]:
        """
        Récupère un administrateur par email.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, niveau_acces, type, date_creation "
            "FROM utilisateur "
            "WHERE email = %(email)s AND type = 'ADMIN'"
        )
        with ConnectionManager().getConnexion() as con:
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
            numero_tel=res["numero_tel"],
            niveau_acces=res["niveau_acces"],
            type=res["type"],
            date_creation=res["date_creation"],
        )

    # ---------- CREATE ----------

    def create(self, admin_in: AdministrateurModelIn) -> AdministrateurModelOut:
        """
        Crée un nouvel administrateur.
        admin_in.mot_de_passe est hashé avant insertion.
        """
        query = (
            "INSERT INTO utilisateur (email, prenom, nom, numero_tel, mot_de_passe, niveau_acces, type, date_creation) "
            "VALUES (%(email)s, %(prenom)s, %(nom)s, %(numero_tel)s, %(mot_de_passe)s, %(niveau_acces)s, 'ADMIN', %(date_creation)s) "
            "RETURNING id_utilisateur"
        )
        now = datetime.now()
        params = {
            "email": admin_in.email,
            "prenom": admin_in.prenom,
            "nom": admin_in.nom,
            "numero_tel": admin_in.numero_tel,
            "mot_de_passe": self._hash_password(admin_in.mot_de_passe),
            "niveau_acces": admin_in.niveau_acces,
            "date_creation": now,
        }

        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                new_id = curs.fetchone()["id_utilisateur"]

        return AdministrateurModelOut(
            id_utilisateur=new_id,
            email=admin_in.email,
            prenom=admin_in.prenom,
            nom=admin_in.nom,
            numero_tel=admin_in.numero_tel,
            niveau_acces=admin_in.niveau_acces,
            type="ADMIN",
            date_creation=now,
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
            "   numero_tel = %(numero_tel)s, "
            "   niveau_acces = %(niveau_acces)s "
            " WHERE id_utilisateur = %(id)s AND type = 'ADMIN' "
            " RETURNING * "
            ") "
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, niveau_acces, type, date_creation "
            "FROM updated"
        )
        params = {
            "id": admin_out.id_utilisateur,
            "email": admin_out.email,
            "prenom": admin_out.prenom,
            "nom": admin_out.nom,
            "numero_tel": admin_out.numero_tel,
            "niveau_acces": admin_out.niveau_acces,
        }

        with ConnectionManager().getConnexion() as con:
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
            numero_tel=res["numero_tel"],
            niveau_acces=res["niveau_acces"],
            type=res["type"],
            date_creation=res["date_creation"],
        )

    # ---------- DELETE ----------

    def delete(self, id_utilisateur: int) -> bool:
        """
        Supprime un administrateur par ID.
        """
        query = "DELETE FROM utilisateur WHERE id_utilisateur = %(id)s AND type = 'ADMIN'"
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_utilisateur})
                return curs.rowcount > 0

    # ---------- AUTH / SECURITY ----------

    def authenticate(self, email: str, mot_de_passe: str) -> Optional[AdministrateurModelOut]:
        """
        Vérifie les identifiants et retourne l'admin si OK, sinon None.
        """
        # On doit lire le hash du mot de passe pour comparer
        query = (
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, mot_de_passe, niveau_acces, type, date_creation "
            "FROM utilisateur WHERE email = %(email)s AND type = 'ADMIN'"
        )
        with ConnectionManager().getConnexion() as con:
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
            numero_tel=res["numero_tel"],
            niveau_acces=res["niveau_acces"],
            type=res["type"],
            date_creation=res["date_creation"],
        )

    def change_password(self, id_utilisateur: int, new_password: str) -> bool:
        """
        Change le mot de passe d'un administrateur (hash bcrypt).
        """
        query = (
            "UPDATE utilisateur SET mot_de_passe = %(pwd)s "
            "WHERE id_utilisateur = %(id)s AND type = 'ADMIN'"
        )
        params = {"pwd": self._hash_password(new_password), "id": id_utilisateur}

        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                return curs.rowcount > 0
