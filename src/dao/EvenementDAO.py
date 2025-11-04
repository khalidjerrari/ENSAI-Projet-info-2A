# dao/evenement_dao.py
from typing import List, Optional
from dao.db_connection import DBConnection
from models.evenement_models import EvenementModelOut, EvenementModelIn


class EvenementDao:
    """
    DAO pour la gestion des événements (schéma conforme à la table 'evenement').

    Colonnes en base :
      id_evenement SERIAL PK
      fk_transport INT NOT NULL
      fk_utilisateur INT NULL
      titre VARCHAR(150) NOT NULL
      adresse VARCHAR(255) NULL
      ville VARCHAR(100) NULL
      date_evenement DATE NOT NULL
      description TEXT NULL
      capacite INT NOT NULL
      date_creation TIMESTAMP DEFAULT NOW()
      categorie VARCHAR(50) NULL
      statut VARCHAR(50) DEFAULT 'pas encore finalisé'
    """

    # ---------- READ ----------

    def find_all(self, limit: int = 100, offset: int = 0) -> List[EvenementModelOut]:
        """
        Récupère une liste paginée d'événements.
        """
        query = (
            "SELECT id_evenement, fk_transport, fk_utilisateur, titre, adresse, ville, "
            "       date_evenement, description, capacite, categorie, statut, date_creation "
            "FROM evenement "
            "ORDER BY id_evenement "
            "LIMIT %(limit)s OFFSET %(offset)s"
        )
        params = {"limit": max(limit, 0), "offset": max(offset, 0)}

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                rows = curs.fetchall()

        events: List[EvenementModelOut] = []
        for r in rows:
            events.append(
                EvenementModelOut(
                    id_evenement=r["id_evenement"],
                    fk_transport=r["fk_transport"],
                    fk_utilisateur=r["fk_utilisateur"],
                    titre=r["titre"],
                    adresse=r["adresse"],
                    ville=r["ville"],
                    date_evenement=r["date_evenement"],
                    description=r["description"],
                    capacite=r["capacite"],
                    categorie=r["categorie"],
                    statut=r["statut"],
                    date_creation=r["date_creation"],
                )
            )
        return events

    def find_by_id(self, id_evenement: int) -> Optional[EvenementModelOut]:
        """
        Récupère un événement par son ID.
        """
        query = (
            "SELECT id_evenement, fk_transport, fk_utilisateur, titre, adresse, ville, "
            "       date_evenement, description, capacite, categorie, statut, date_creation "
            "FROM evenement "
            "WHERE id_evenement = %(id)s"
        )
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_evenement})
                r = curs.fetchone()

        if r is None:
            return None

        return EvenementModelOut(
            id_evenement=r["id_evenement"],
            fk_transport=r["fk_transport"],
            fk_utilisateur=r["fk_utilisateur"],
            titre=r["titre"],
            adresse=r["adresse"],
            ville=r["ville"],
            date_evenement=r["date_evenement"],
            description=r["description"],
            capacite=r["capacite"],
            categorie=r["categorie"],
            statut=r["statut"],
            date_creation=r["date_creation"],
        )

    def find_by_transport(self, fk_transport: int, limit: int = 100, offset: int = 0) -> List[EvenementModelOut]:
        """
        (Optionnel) Liste des événements liés à un transport.
        """
        query = (
            "SELECT id_evenement, fk_transport, fk_utilisateur, titre, adresse, ville, "
            "       date_evenement, description, capacite, categorie, statut, date_creation "
            "FROM evenement "
            "WHERE fk_transport = %(fk_transport)s "
            "ORDER BY date_evenement, id_evenement "
            "LIMIT %(limit)s OFFSET %(offset)s"
        )
        params = {
            "fk_transport": fk_transport,
            "limit": max(limit, 0),
            "offset": max(offset, 0),
        }

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                rows = curs.fetchall()

        return [
            EvenementModelOut(
                id_evenement=r["id_evenement"],
                fk_transport=r["fk_transport"],
                fk_utilisateur=r["fk_utilisateur"],
                titre=r["titre"],
                adresse=r["adresse"],
                ville=r["ville"],
                date_evenement=r["date_evenement"],
                description=r["description"],
                capacite=r["capacite"],
                categorie=r["categorie"],
                statut=r["statut"],
                date_creation=r["date_creation"],
            )
            for r in rows
        ]

    # ---------- CREATE ----------

    def create(self, evenement_in: EvenementModelIn) -> EvenementModelOut:
        """
        Crée un nouvel événement. Laisse la base renseigner date_creation (DEFAULT NOW()).
        """
        query = (
            "INSERT INTO evenement (fk_transport, fk_utilisateur, titre, adresse, ville, date_evenement, "
            "                        description, capacite, categorie, statut) "
            "VALUES (%(fk_transport)s, %(fk_utilisateur)s, %(titre)s, %(adresse)s, %(ville)s, %(date_evenement)s, "
            "        %(description)s, %(capacite)s, %(categorie)s, %(statut)s) "
            "RETURNING id_evenement, date_creation"
        )
        params = {
            "fk_transport": evenement_in.fk_transport,
            "fk_utilisateur": evenement_in.fk_utilisateur,
            "titre": evenement_in.titre,
            "adresse": evenement_in.adresse,
            "ville": evenement_in.ville,
            "date_evenement": evenement_in.date_evenement,
            "description": evenement_in.description,
            "capacite": evenement_in.capacite,
            "categorie": evenement_in.categorie,
            "statut": evenement_in.statut,
        }

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                row = curs.fetchone()

        return EvenementModelOut(
            id_evenement=row["id_evenement"],
            fk_transport=evenement_in.fk_transport,
            fk_utilisateur=evenement_in.fk_utilisateur,
            titre=evenement_in.titre,
            adresse=evenement_in.adresse,
            ville=evenement_in.ville,
            date_evenement=evenement_in.date_evenement,
            description=evenement_in.description,
            capacite=evenement_in.capacite,
            categorie=evenement_in.categorie,
            statut=evenement_in.statut,
            date_creation=row["date_creation"],
        )

    # ---------- UPDATE ----------

    def update(self, evenement: EvenementModelOut) -> Optional[EvenementModelOut]:
        """
        Met à jour un événement existant (toutes colonnes modifiables sauf PK/date_creation).
        """
        query = (
            "WITH updated AS ( "
            "  UPDATE evenement SET "
            "     fk_transport = %(fk_transport)s, "
            "     fk_utilisateur = %(fk_utilisateur)s, "
            "     titre = %(titre)s, "
            "     adresse = %(adresse)s, "
            "     ville = %(ville)s, "
            "     date_evenement = %(date_evenement)s, "
            "     description = %(description)s, "
            "     capacite = %(capacite)s, "
            "     categorie = %(categorie)s, "
            "     statut = %(statut)s "
            "  WHERE id_evenement = %(id_evenement)s "
            "  RETURNING id_evenement, fk_transport, fk_utilisateur, titre, adresse, ville, "
            "            date_evenement, description, capacite, categorie, statut, date_creation "
            ") "
            "SELECT * FROM updated"
        )
        params = {
            "id_evenement": evenement.id_evenement,
            "fk_transport": evenement.fk_transport,
            "fk_utilisateur": evenement.fk_utilisateur,
            "titre": evenement.titre,
            "adresse": evenement.adresse,
            "ville": evenement.ville,
            "date_evenement": evenement.date_evenement,
            "description": evenement.description,
            "capacite": evenement.capacite,
            "categorie": evenement.categorie,
            "statut": evenement.statut,
        }

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                r = curs.fetchone()

        if r is None:
            return None

        return EvenementModelOut(
            id_evenement=r["id_evenement"],
            fk_transport=r["fk_transport"],
            fk_utilisateur=r["fk_utilisateur"],
            titre=r["titre"],
            adresse=r["adresse"],
            ville=r["ville"],
            date_evenement=r["date_evenement"],
            description=r["description"],
            capacite=r["capacite"],
            categorie=r["categorie"],
            statut=r["statut"],
            date_creation=r["date_creation"],
        )

    # ---------- DELETE ----------

    def delete(self, id_evenement: int) -> bool:
        """
        Supprime un événement par son ID.
        """
        query = "DELETE FROM evenement WHERE id_evenement = %(id)s"
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_evenement})
                return curs.rowcount > 0
