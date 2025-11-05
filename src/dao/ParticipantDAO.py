# dao/participant_dao.py
from typing import List, Optional
import bcrypt

from dao.db_connection import DBConnection
from model.participant_models import ParticipantModelIn, ParticipantModelOut


class ParticipantDao:
    """
    DAO pour la gestion des participants (utilisateur.administrateur = FALSE).
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
    def find_all(self, limit: int = 100, offset: int = 0) -> List[ParticipantModelOut]:
        """
        Récupère une liste paginée de participants.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, telephone, administrateur, date_creation "
            "FROM utilisateur "
            "WHERE administrateur = FALSE "
            "ORDER BY id_utilisateur "
            "LIMIT %(limit)s OFFSET %(offset)s"
        )
        params = {"limit": max(limit, 0), "offset": max(offset, 0)}

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                rows = curs.fetchall()

        participants: List[ParticipantModelOut] = []
        for r in rows:
            participants.append(
                ParticipantModelOut(
                    id_utilisateur=r["id_utilisateur"],
                    email=r["email"],
                    prenom=r["prenom"],
                    nom=r["nom"],
                    telephone=r["telephone"],
                    administrateur=r["administrateur"],
                    date_creation=r["date_creation"],
                )
            )
        return participants

    def find_by_id(self, id_utilisateur: int) -> Optional[ParticipantModelOut]:
        """
        Récupère un participant par ID.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, telephone, administrateur, date_creation "
            "FROM utilisateur "
            "WHERE id_utilisateur = %(id)s AND administrateur = FALSE"
        )
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_utilisateur})
                r = curs.fetchone()

        if r is None:
            return None

        return ParticipantModelOut(
            id_utilisateur=r["id_utilisateur"],
            email=r["email"],
            prenom=r["prenom"],
            nom=r["nom"],
            telephone=r["telephone"],
            administrateur=r["administrateur"],
            date_creation=r["date_creation"],
        )

    def find_by_email(self, email: str) -> Optional[ParticipantModelOut]:
        """
        Récupère un participant par email.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, telephone, administrateur, date_creation "
            "FROM utilisateur "
            "WHERE email = %(email)s AND administrateur = FALSE"
        )
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"email": email})
                r = curs.fetchone()

        if r is None:
            return None

        return ParticipantModelOut(
            id_utilisateur=r["id_utilisateur"],
            email=r["email"],
            prenom=r["prenom"],
            nom=r["nom"],
            telephone=r["telephone"],
            administrateur=r["administrateur"],
            date_creation=r["date_creation"],
        )

    # ---------- CREATE ----------
    def create(self, participant_in: ParticipantModelIn) -> ParticipantModelOut:
        """
        Crée un nouveau participant (administrateur=FALSE).
        Laisse la BDD remplir date_creation (DEFAULT CURRENT_TIMESTAMP).
        """
        query = (
            "INSERT INTO utilisateur (email, prenom, nom, telephone, mot_de_passe, administrateur) "
            "VALUES (%(email)s, %(prenom)s, %(nom)s, %(telephone)s, %(mot_de_passe)s, FALSE) "
            "RETURNING id_utilisateur, date_creation"
        )
        params = {
            "email": participant_in.email,
            "prenom": participant_in.prenom,
            "nom": participant_in.nom,
            "telephone": participant_in.telephone,
            "mot_de_passe": self._hash_password(participant_in.mot_de_passe),
        }

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                row = curs.fetchone()

        return ParticipantModelOut(
            id_utilisateur=row["id_utilisateur"],
            email=participant_in.email,
            prenom=participant_in.prenom,
            nom=participant_in.nom,
            telephone=participant_in.telephone,
            administrateur=False,
            date_creation=row["date_creation"],
        )

    # ---------- UPDATE ----------
    def update(self, participant_out: ParticipantModelOut) -> Optional[ParticipantModelOut]:
        """
        Met à jour les informations d’un participant (hors mot de passe).
        """
        query = (
            "WITH updated AS ("
            "  UPDATE utilisateur SET "
            "    email = %(email)s, "
            "    prenom = %(prenom)s, "
            "    nom = %(nom)s, "
            "    telephone = %(telephone)s "
            "  WHERE id_utilisateur = %(id)s AND administrateur = FALSE "
            "  RETURNING id_utilisateur, email, prenom, nom, telephone, administrateur, date_creation"
            ") "
            "SELECT * FROM updated"
        )
        params = {
            "id": participant_out.id_utilisateur,
            "email": participant_out.email,
            "prenom": participant_out.prenom,
            "nom": participant_out.nom,
            "telephone": participant_out.telephone,
        }

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                r = curs.fetchone()

        if r is None:
            return None

        return ParticipantModelOut(
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
        Supprime un participant par son ID.
        """
        query = "DELETE FROM utilisateur WHERE id_utilisateur = %(id)s AND administrateur = FALSE"
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_utilisateur})
                return curs.rowcount > 0

    # ---------- AUTH ----------
    def authenticate(self, email: str, mot_de_passe: str) -> Optional[ParticipantModelOut]:
        """
        Authentifie un participant par email/mot de passe.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, telephone, mot_de_passe, administrateur, date_creation "
            "FROM utilisateur "
            "WHERE email = %(email)s AND administrateur = FALSE"
        )
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"email": email})
                r = curs.fetchone()

        if r is None or not self._check_password(mot_de_passe, r["mot_de_passe"]):
            return None

        return ParticipantModelOut(
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
        Met à jour le mot de passe (hash bcrypt) du participant.
        """
        query = (
            "UPDATE utilisateur SET mot_de_passe = %(pwd)s "
            "WHERE id_utilisateur = %(id)s AND administrateur = FALSE"
        )
        params = {"pwd": self._hash_password(new_password), "id": id_utilisateur}

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                return curs.rowcount > 0
