# dao/bus_dao.py
from typing import List, Optional

from dao.db_connection import DBConnection
from model.creneau_bus import CreneauBus


class CreneauBusDao:
    """
    DAO pour la gestion des créneaux de bus (table `bus`).
    Schéma:
      id_bus SERIAL PK
      fk_evenement INT REFERENCES evenement(id_evenement) ON DELETE SET NULL
      matricule VARCHAR(20)
      nombre_places INT NOT NULL CHECK (nombre_places > 0)
      direction VARCHAR(10) IN ('aller','retour') DEFAULT 'aller'
      description VARCHAR(100) UNIQUE NOT NULL
    """

    # ------------- HELPERS -------------
    @staticmethod
    def _row_to_model(row: dict) -> CreneauBus:
        # Le DAO ne gère pas `inscrits` (logique métier) -> 0 par défaut ici
        return CreneauBus(
            id_bus=row.get("id_bus"),
            fk_evenement=row.get("fk_evenement"),
            matricule=row.get("matricule"),
            description=row.get("description"),
            nombre_places=row.get("nombre_places"),
            direction=row.get("direction"),
            inscrits=0,
        )

    # ------------- CREATE -------------
    def create(self, bus: CreneauBus) -> Optional[CreneauBus]:
        """
        Insère un bus et renvoie l'objet complété (id_bus, etc.).
        """
        query = """
            INSERT INTO bus (fk_evenement, matricule, nombre_places, direction, description)
            VALUES (%(fk_evenement)s, %(matricule)s, %(nombre_places)s, %(direction)s, %(description)s)
            RETURNING id_bus, fk_evenement, matricule, nombre_places, direction, description
        """
        params = {
            "fk_evenement": bus.fk_evenement,
            "matricule": bus.matricule,
            "nombre_places": bus.nombre_places,
            "direction": bus.direction,
            "description": bus.description,
        }

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                try:
                    curs.execute(query, params)
                    row = curs.fetchone()
                    con.commit()
                except Exception as e:
                    con.rollback()
                    print(f"Erreur DAO (create bus): {e}")
                    return None

        return self._row_to_model(row)

    # ------------- READ -------------
    def find_by_id(self, id_bus: int) -> Optional[CreneauBus]:
        query = """
            SELECT id_bus, fk_evenement, matricule, nombre_places, direction, description
            FROM bus
            WHERE id_bus = %(id)s
        """
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_bus})
                row = curs.fetchone()
        return self._row_to_model(row) if row else None

    def find_by_event(self, id_evenement: int) -> List[CreneauBus]:
        query = """
            SELECT id_bus, fk_evenement, matricule, nombre_places, direction, description
            FROM bus
            WHERE fk_evenement = %(id_evenement)s
            ORDER BY id_bus
        """
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id_evenement": id_evenement})
                rows = curs.fetchall()
        return [self._row_to_model(r) for r in rows]

    def find_by_description(self, description: str) -> Optional[CreneauBus]:
        query = """
            SELECT id_bus, fk_evenement, matricule, nombre_places, direction, description
            FROM bus
            WHERE description = %(description)s
        """
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"description": description})
                row = curs.fetchone()
        return self._row_to_model(row) if row else None

    def find_all(self, limit: int = 100, offset: int = 0) -> List[CreneauBus]:
        query = """
            SELECT id_bus, fk_evenement, matricule, nombre_places, direction, description
            FROM bus
            ORDER BY id_bus
            LIMIT %(limit)s OFFSET %(offset)s
        """
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"limit": max(0, limit), "offset": max(0, offset)})
                rows = curs.fetchall()
        return [self._row_to_model(r) for r in rows]

    # ------------- UPDATE -------------
    def update(self, bus: CreneauBus) -> Optional[CreneauBus]:
        """
        Met à jour un bus (tous champs sauf id).
        Nécessite bus.id_bus.
        """
        if bus.id_bus is None:
            raise ValueError("id_bus requis pour update().")

        query = """
            WITH updated AS (
                UPDATE bus
                SET fk_evenement = %(fk_evenement)s,
                    matricule    = %(matricule)s,
                    nombre_places= %(nombre_places)s,
                    direction    = %(direction)s,
                    description  = %(description)s
                WHERE id_bus = %(id_bus)s
                RETURNING id_bus, fk_evenement, matricule, nombre_places, direction, description
            )
            SELECT * FROM updated
        """
        params = {
            "id_bus": bus.id_bus,
            "fk_evenement": bus.fk_evenement,
            "matricule": bus.matricule,
            "nombre_places": bus.nombre_places,
            "direction": bus.direction,
            "description": bus.description,
        }

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                try:
                    curs.execute(query, params)
                    row = curs.fetchone()
                    con.commit()
                except Exception as e:
                    con.rollback()
                    print(f"Erreur DAO (update bus): {e}")
                    return None

        return self._row_to_model(row) if row else None

    def update_places(self, id_bus: int, nombre_places: int) -> Optional[CreneauBus]:
        """
        Met à jour uniquement le nombre de places.
        """
        query = """
            WITH updated AS (
                UPDATE bus
                SET nombre_places = %(nombre_places)s
                WHERE id_bus = %(id_bus)s
                RETURNING id_bus, fk_evenement, matricule, nombre_places, direction, description
            )
            SELECT * FROM updated
        """
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                try:
                    curs.execute(query, {"id_bus": id_bus, "nombre_places": nombre_places})
                    row = curs.fetchone()
                    con.commit()
                except Exception as e:
                    con.rollback()
                    print(f"Erreur DAO (update_places): {e}")
                    return None

        return self._row_to_model(row) if row else None

    # ------------- DELETE -------------
    def delete(self, id_bus: int) -> bool:
        query = "DELETE FROM bus WHERE id_bus = %(id)s"
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_bus})
                return curs.rowcount > 0

    # ------------- UTILS -------------
    def count_for_event(self, id_evenement: int) -> int:
        """
        Nombre de bus rattachés à un événement.
        """
        query = "SELECT COUNT(*) AS c FROM bus WHERE fk_evenement = %(id)s"
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_evenement})
                row = curs.fetchone()
        return int(row["c"]) if row else 0

    def exists_description(self, description: str) -> bool:
        """
        Vérifie l'existence d'une description (contrainte UNIQUE).
        """
        query = "SELECT 1 FROM bus WHERE description = %(desc)s LIMIT 1"
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"desc": description})
                return curs.fetchone() is not None
