from typing import List, Optional, Dict, Any
from datetime import date

from psycopg2.extras import RealDictCursor

from dao.db_connection import DBConnection
from model.evenement_models import EvenementModelOut


class ConsultationEvenementDao:
    """
    DAO de consultation (lecture seule) des événements.
    Minimalement adapté au nouveau schéma SQL (suppression de fk_transport, comptage par événement).
    """

    # ---------- Listes simples ----------

    def lister_tous(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "date_evenement ASC, id_evenement ASC",
    ) -> List[EvenementModelOut]:
        """
        Liste paginée de tous les événements.
        """
        query = (
            "SELECT id_evenement, fk_utilisateur, titre, adresse, ville, "
            "       date_evenement, description, capacite, categorie, statut, date_creation "
            "FROM evenement "
            f"ORDER BY {order_by} "
            "LIMIT %(limit)s OFFSET %(offset)s"
        )
        params = {"limit": max(limit, 0), "offset": max(offset, 0)}

        with DBConnection().getConnexion() as con:
            with con.cursor(cursor_factory=RealDictCursor) as curs:
                curs.execute(query, params)
                rows = curs.fetchall()

        return [EvenementModelOut(**row) for row in rows]

    def lister_disponibles(
        self,
        limit: int = 100,
        offset: int = 0,
        a_partir_du: Optional[date] = None,
    ) -> List[EvenementModelOut]:
        """
        Liste des événements au statut 'disponible en ligne'.
        Optionnel: ne renvoyer qu'à partir d'une date (incluse).
        """
        where = ["statut = 'disponible en ligne'"]
        params: Dict[str, Any] = {"limit": max(limit, 0), "offset": max(offset, 0)}

        if a_partir_du is not None:
            where.append("date_evenement >= %(dmin)s")
            params["dmin"] = a_partir_du

        query = (
            "SELECT id_evenement, fk_utilisateur, titre, adresse, ville, "
            "       date_evenement, description, capacite, categorie, statut, date_creation "
            "FROM evenement "
            f"WHERE {' AND '.join(where)} "
            "ORDER BY date_evenement ASC, id_evenement ASC "
            "LIMIT %(limit)s OFFSET %(offset)s"
        )

        with DBConnection().getConnexion() as con:
            with con.cursor(cursor_factory=RealDictCursor) as curs:
                curs.execute(query, params)
                rows = curs.fetchall()

        return [EvenementModelOut(**row) for row in rows]

    # ---------- Recherche avec filtres ----------

    def rechercher(
        self,
        ville: Optional[str] = None,
        categorie: Optional[str] = None,
        statut: Optional[str] = None,
        date_min: Optional[date] = None,
        date_max: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[EvenementModelOut]:
        """
        Recherche d'événements avec filtres facultatifs.
        - ville : filtre ILIKE '%ville%'
        - categorie : égalité stricte
        - statut : égalité stricte
        - date_min / date_max : intervalle fermé [date_min, date_max]
        """
        where = []
        params: Dict[str, Any] = {"limit": max(limit, 0), "offset": max(offset, 0)}

        if ville:
            where.append("ville ILIKE %(ville)s")
            params["ville"] = f"%{ville}%"
        if categorie:
            where.append("categorie = %(categorie)s")
            params["categorie"] = categorie
        if statut:
            where.append("statut = %(statut)s")
            params["statut"] = statut
        if date_min:
            where.append("date_evenement >= %(date_min)s")
            params["date_min"] = date_min
        if date_max:
            where.append("date_evenement <= %(date_max)s")
            params["date_max"] = date_max

        where_clause = f"WHERE {' AND '.join(where)} " if where else ""
        query = (
            "SELECT id_evenement, fk_utilisateur, titre, adresse, ville, "
            "       date_evenement, description, capacite, categorie, statut, date_creation "
            "FROM evenement "
            f"{where_clause}"
            "ORDER BY date_evenement ASC, id_evenement ASC "
            "LIMIT %(limit)s OFFSET %(offset)s"
        )

        with DBConnection().getConnexion() as con:
            with con.cursor(cursor_factory=RealDictCursor) as curs:
                curs.execute(query, params)
                rows = curs.fetchall()

        return [EvenementModelOut(**row) for row in rows]

    # ---------- Avec places restantes ----------

    def lister_avec_places_restantes(
        self,
        limit: int = 100,
        offset: int = 0,
        seulement_disponibles: bool = True,
        a_partir_du: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Liste des événements avec le calcul des places restantes :
        places_restantes = capacite - COUNT(reservation.id_reservation) pour l'événement.

        Retourne des dicts : {**EvenementModelOut fields..., "places_restantes": int}
        """
        where = []
        params: Dict[str, Any] = {"limit": max(limit, 0), "offset": max(offset, 0)}

        if seulement_disponibles:
            where.append("e.statut = 'disponible en ligne'")
        if a_partir_du is not None:
            where.append("e.date_evenement >= %(dmin)s")
            params["dmin"] = a_partir_du

        where_clause = f"WHERE {' AND '.join(where)} " if where else ""

        # Comptage des réservations par événement (nouveau schéma)
        query = (
            "WITH resa AS ( "
            "  SELECT fk_evenement, COUNT(*) AS nb_resa "
            "  FROM reservation "
            "  GROUP BY fk_evenement "
            ") "
            "SELECT e.id_evenement, e.fk_utilisateur, e.titre, e.adresse, e.ville, "
            "       e.date_evenement, e.description, e.capacite, e.categorie, e.statut, e.date_creation, "
            "       (e.capacite - COALESCE(r.nb_resa, 0)) AS places_restantes "
            "FROM evenement e "
            "LEFT JOIN resa r ON r.fk_evenement = e.id_evenement "
            f"{where_clause}"
            "ORDER BY e.date_evenement ASC, e.id_evenement ASC "
            "LIMIT %(limit)s OFFSET %(offset)s"
        )

        with DBConnection().getConnexion() as con:
            with con.cursor(cursor_factory=RealDictCursor) as curs:
                curs.execute(query, params)
                rows = curs.fetchall()

        # rows est déjà une liste de dicts (RealDictCursor)
        return [dict(row) for row in rows]
