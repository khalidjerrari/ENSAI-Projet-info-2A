# dao/participant_dao.py
from typing import List, Optional
from datetime import datetime
import bcrypt

from dao.connection_manager import ConnectionManager
from models.participant_models import ParticipantModelIn, ParticipantModelOut


class ParticipantDao:
    """
    DAO pour la gestion des participants dans la base de données.

    Table supposée : 'utilisateur'
    Colonnes :
        id_utilisateur (PK), email (unique), prenom, nom,
        numero_tel, mot_de_passe, niveau_acces, type ('PARTICIPANT'),
        date_creation
    """

    # ---------- Helpers pour le mot de passe ----------
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

    # ---------- CRUD ----------
    def find_all(self, limit: int = 100, offset: int = 0) -> List[ParticipantModelOut]:
        """
        Récupère une liste paginée de participants.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, niveau_acces, type, date_creation "
            "FROM utilisateur "
            "WHERE type = 'PARTICIPANT' "
            "ORDER BY id_utilisateur "
            f"LIMIT {max(limit, 0)} OFFSET {max(offset, 0)}"
        )

        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query)
                rows = curs.fetchall()

        participants: List[ParticipantModelOut] = []
        for r in rows:
            participants.append(
                ParticipantModelOut(
                    id_utilisateur=r["id_utilisateur"],
                    email=r["email"],
                    prenom=r["prenom"],
                    nom=r["nom"],
                    numero_tel=r["numero_tel"],
                    niveau_acces=r["niveau_acces"],
                    type=r["type"],
                    date_creation=r["date_creation"],
                )
            )
        return participants

    def find_by_id(self, id_utilisateur: int) -> Optional[ParticipantModelOut]:
        """
        Récupère un participant par ID.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, niveau_acces, type, date_creation "
            "FROM utilisateur "
            "WHERE id_utilisateur = %(id)s AND type = 'PARTICIPANT'"
        )

        with ConnectionManager().getConnexion() as con:
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
            numero_tel=r["numero_tel"],
            niveau_acces=r["niveau_acces"],
            type=r["type"],
            date_creation=r["date_creation"],
        )

    def find_by_email(self, email: str) -> Optional[ParticipantModelOut]:
        """
        Récupère un participant par email.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, niveau_acces, type, date_creation "
            "FROM utilisateur "
            "WHERE email = %(email)s AND type = 'PARTICIPANT'"
        )

        with ConnectionManager().getConnexion() as con:
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
            numero_tel=r["numero_tel"],
            niveau_acces=r["niveau_acces"],
            type=r["type"],
            date_creation=r["date_creation"],
        )

    def create(self, participant_in: ParticipantModelIn) -> ParticipantModelOut:
        """
        Crée un nouveau participant dans la base de données.
        """
        query = (
            "INSERT INTO utilisateur (email, prenom, nom, numero_tel, mot_de_passe, niveau_acces, type, date_creation) "
            "VALUES (%(email)s, %(prenom)s, %(nom)s, %(numero_tel)s, %(mot_de_passe)s, %(niveau_acces)s, 'PARTICIPANT', %(date_creation)s) "
            "RETURNING id_utilisateur"
        )

        now = datetime.now()
        params = {
            "email": participant_in.email,
            "prenom": participant_in.prenom,
            "nom": participant_in.nom,
            "numero_tel": participant_in.numero_tel,
            "mot_de_passe": self._hash_password(participant_in.mot_de_passe),
            "niveau_acces": participant_in.niveau_acces,
            "date_creation": now,
        }

        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                new_id = curs.fetchone()["id_utilisateur"]

        return ParticipantModelOut(
            id_utilisateur=new_id,
            email=participant_in.email,
            prenom=participant_in.prenom,
            nom=participant_in.nom,
            numero_tel=participant_in.numero_tel,
            niveau_acces=participant_in.niveau_acces,
            type="PARTICIPANT",
            date_creation=now,
        )

    def update(self, participant_out: ParticipantModelOut) -> Optional[ParticipantModelOut]:
        """
        Met à jour les informations d’un participant.
        """
        query = (
            "WITH updated AS ("
            "  UPDATE utilisateur SET "
            "    email = %(email)s, "
            "    prenom = %(prenom)s, "
            "    nom = %(nom)s, "
            "    numero_tel = %(numero_tel)s, "
            "    niveau_acces = %(niveau_acces)s "
            "  WHERE id_utilisateur = %(id)s AND type = 'PARTICIPANT' "
            "  RETURNING *"
            ") "
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, niveau_acces, type, date_creation "
            "FROM updated"
        )

        params = {
            "id": participant_out.id_utilisateur,
            "email": participant_out.email,
            "prenom": participant_out.prenom,
            "nom": participant_out.nom,
            "numero_tel": participant_out.numero_tel,
            "niveau_acces": participant_out.niveau_acces,
        }

        with ConnectionManager().getConnexion() as con:
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
            numero_tel=r["numero_tel"],
            niveau_acces=r["niveau_acces"],
            type=r["type"],
            date_creation=r["date_creation"],
        )

    def delete(self, id_utilisateur: int) -> bool:
        """
        Supprime un participant par son ID.
        """
        query = "DELETE FROM utilisateur WHERE id_utilisateur = %(id)s AND type = 'PARTICIPANT'"

        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_utilisateur})
                return curs.rowcount > 0

    # ---------- AUTH / PASSWORD ----------
    def authenticate(self, email: str, mot_de_passe: str) -> Optional[ParticipantModelOut]:
        """
        Authentifie un participant via son email et son mot de passe.
        """
        query = (
            "SELECT id_utilisateur, email, prenom, nom, numero_tel, mot_de_passe, niveau_acces, type, date_creation "
            "FROM utilisateur "
            "WHERE email = %(email)s AND type = 'PARTICIPANT'"
        )

        with ConnectionManager().getConnexion() as con:
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
            numero_tel=r["numero_tel"],
            niveau_acces=r["niveau_acces"],
            type=r["type"],
            date_creation=r["date_creation"],
        )

    def change_password(self, id_utilisateur: int, new_password: str) -> bool:
        """
        Met à jour le mot de passe (hash bcrypt) du participant.
        """
        query = (
            "UPDATE utilisateur SET mot_de_passe = %(pwd)s "
            "WHERE id_utilisateur = %(id)s AND type = 'PARTICIPANT'"
        )

        params = {"pwd": self._hash_password(new_password), "id": id_utilisateur}

        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                return curs.rowcount > 0
