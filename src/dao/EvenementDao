from typing import List, Optional
from datetime import datetime
from dao.connection_manager import ConnectionManager
from models.evenement_models import EvenementModelOut, EvenementModelIn


class EvenementDao:
    """
    DAO pour la gestion des événements dans la base de données.
    """

    def find_all(self, limit: int = 100, offset: int = 0) -> List[EvenementModelOut]:
        """
        Récupère une liste paginée d'événements.

        Args:
            limit (int): nombre maximum d'événements retournés.
            offset (int): nombre d'événements à sauter pour la pagination.

        Returns:
            List[EvenementModelOut]: liste d'événements.
        """
        query = (
            "SELECT id_event, titre, description, categorie, statut, capacite, prix_base, prix_sam, prix_adherent, "
            "id_admin_createur, date_creation "
            "FROM evenement "
            "ORDER BY id_event "
            f"LIMIT {max(limit,0)} OFFSET {max(offset,0)}"
        )
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query)
                results = curs.fetchall()

        evenements = []
        for res in results:
            event = EvenementModelOut(
                id_event=res["id_event"],
                titre=res["titre"],
                description=res["description"],
                categorie=res["categorie"],
                statut=res["statut"],
                capacite=res["capacite"],
                prixBase=res["prix_base"],
                prixSam=res["prix_sam"],
                prixAdherent=res["prix_adherent"],
                creerPar_id=res["id_admin_createur"],
                date_creation=res["date_creation"]
            )
            evenements.append(event)
        return evenements

    def find_by_id(self, id_event: int) -> Optional[EvenementModelOut]:
        """
        Récupère un événement par son ID.

        Args:
            id_event (int): Identifiant de l'événement.

        Returns:
            EvenementModelOut | None: événement si trouvé, sinon None.
        """
        query = (
            "SELECT id_event, titre, description, categorie, statut, capacite, prix_base, prix_sam, prix_adherent, "
            "id_admin_createur, date_creation "
            "FROM evenement WHERE id_event = %(id_event)s"
        )
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id_event": id_event})
                res = curs.fetchone()

        if res is None:
            return None
        
        return EvenementModelOut(
            id_event=res["id_event"],
            titre=res["titre"],
            description=res["description"],
            categorie=res["categorie"],
            statut=res["statut"],
            capacite=res["capacite"],
            prixBase=res["prix_base"],
            prixSam=res["prix_sam"],
            prixAdherent=res["prix_adherent"],
            creerPar_id=res["id_admin_createur"],
            date_creation=res["date_creation"]
        )

    def create(self, evenement_in: EvenementModelIn) -> EvenementModelOut:
        """
        Crée un nouvel événement dans la base.

        Args:
            evenement_in (EvenementModelIn): données d'entrée de l'événement.

        Returns:
            EvenementModelOut: événement créé avec ID.
        """
        query = (
            "INSERT INTO evenement (titre, description, categorie, statut, capacite, prix_base, prix_sam, prix_adherent, id_admin_createur, date_creation) "
            "VALUES (%(titre)s, %(description)s, %(categorie)s, %(statut)s, %(capacite)s, %(prixBase)s, %(prixSam)s, %(prixAdherent)s, %(creerPar_id)s, %(date_creation)s) "
            "RETURNING id_event"
        )
        now = datetime.now()
        params = {
            "titre": evenement_in.titre,
            "description": evenement_in.description,
            "categorie": evenement_in.categorie,
            "statut": evenement_in.statut,
            "capacite": evenement_in.capacite,
            "prixBase": evenement_in.prixBase,
            "prixSam": evenement_in.prixSam,
            "prixAdherent": evenement_in.prixAdherent,
            "creerPar_id": evenement_in.creerPar_id,
            "date_creation": now,
        }

        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                new_id = curs.fetchone()["id_event"]

        return EvenementModelOut(
            id_event=new_id,
            titre=evenement_in.titre,
            description=evenement_in.description,
            categorie=evenement_in.categorie,
            statut=evenement_in.statut,
            capacite=evenement_in.capacite,
            prixBase=evenement_in.prixBase,
            prixSam=evenement_in.prixSam,
            prixAdherent=evenement_in.prixAdherent,
            creerPar_id=evenement_in.creerPar_id,
            date_creation=now,
        )

    def update(self, evenement: EvenementModelOut) -> Optional[EvenementModelOut]:
        """
        Met à jour un événement existant.

        Args:
            evenement (EvenementModelOut): événement avec les nouvelles données (doit avoir un id_event valide).

        Returns:
            EvenementModelOut | None: événement mis à jour, ou None si introuvable.
        """
        query = (
            "WITH updated AS ("
            " UPDATE evenement SET "
            "titre = %(titre)s, description = %(description)s, categorie = %(categorie)s, statut = %(statut)s, "
            "capacite = %(capacite)s, prix_base = %(prixBase)s, prix_sam = %(prixSam)s, prix_adherent = %(prixAdherent)s "
            "WHERE id_event = %(id_event)s "
            "RETURNING *) "
            "SELECT id_event, titre, description, categorie, statut, capacite, prix_base, prix_sam, prix_adherent, id_admin_createur, date_creation "
            "FROM updated"
        )
        params = {
            "id_event": evenement.id_event,
            "titre": evenement.titre,
            "description": evenement.description,
            "categorie": evenement.categorie,
            "statut": evenement.statut,
            "capacite": evenement.capacite,
            "prixBase": evenement.prixBase,
            "prixSam": evenement.prixSam,
            "prixAdherent": evenement.prixAdherent,
        }
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                res = curs.fetchone()

        if res is None:
            return None

        return EvenementModelOut(
            id_event=res["id_event"],
            titre=res["titre"],
            description=res["description"],
            categorie=res["categorie"],
            statut=res["statut"],
            capacite=res["capacite"],
            prixBase=res["prix_base"],
            prixSam=res["prix_sam"],
            prixAdherent=res["prix_adherent"],
            creerPar_id=res["id_admin_createur"],
            date_creation=res["date_creation"]
        )

    def delete(self, id_event: int) -> bool:
        """
        Supprime un événement par son ID.

        Args:
            id_event (int): identifiant de l'événement à supprimer.

        Returns:
            bool: True si suppression effectuée, False sinon.
        """
        query = "DELETE FROM evenement WHERE id_event = %(id_event)s"
        with ConnectionManager().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id_event": id_event})
                return curs.rowcount > 0
