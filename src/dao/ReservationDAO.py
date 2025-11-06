# dao/reservation_dao.py
from typing import List, Optional
from dao.db_connection import DBConnection
from model.reservation_models import ReservationModelOut, ReservationModelIn

class ReservationDao:
    """
    DAO pour la gestion des réservations (table 'reservation').
    Schéma pris en compte (PostgreSQL) :
      id_reservation SERIAL PK
      fk_utilisateur INT NOT NULL REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE
      fk_evenement  INT NOT NULL REFERENCES evenement(id_evenement) ON DELETE CASCADE
      bus_aller BOOLEAN DEFAULT FALSE
      bus_retour BOOLEAN DEFAULT FALSE
      date_reservation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      adherent BOOLEAN DEFAULT FALSE
      sam BOOLEAN DEFAULT FALSE
      boisson BOOLEAN DEFAULT FALSE
      CONSTRAINT reservation_unique UNIQUE (fk_utilisateur)
    """

    # ---------- READ ----------
    def find_by_user(self, id_utilisateur: int) -> List[ReservationModelOut]:
        """
        Récupère toutes les réservations d’un utilisateur donné.
        """
        query = """
            SELECT r.id_reservation,
                   r.fk_utilisateur,
                   r.fk_evenement,
                   r.bus_aller,
                   r.bus_retour,
                   r.adherent,
                   r.sam,
                   r.boisson,
                   r.date_reservation
            FROM reservation r
            WHERE r.fk_utilisateur = %(id_utilisateur)s
            ORDER BY r.date_reservation DESC
        """
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id_utilisateur": id_utilisateur})
                rows = curs.fetchall()

        return [
            ReservationModelOut(
                id_reservation=r["id_reservation"],
                fk_utilisateur=r["fk_utilisateur"],
                fk_evenement=r["fk_evenement"],
                bus_aller=r["bus_aller"],
                bus_retour=r["bus_retour"],
                adherent=r["adherent"],
                sam=r["sam"],
                boisson=r["boisson"],
                date_reservation=r["date_reservation"],
            )
            for r in rows
        ]

    def find_by_event(self, id_evenement: int) -> List[ReservationModelOut]:
        """
        Récupère toutes les réservations d’un événement donné.
        Utile pour la liste d’inscrits / comptage.
        """
        query = """
            SELECT r.id_reservation,
                   r.fk_utilisateur,
                   r.fk_evenement,
                   r.bus_aller,
                   r.bus_retour,
                   r.adherent,
                   r.sam,
                   r.boisson,
                   r.date_reservation
            FROM reservation r
            WHERE r.fk_evenement = %(id_evenement)s
            ORDER BY r.date_reservation DESC
        """
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id_evenement": id_evenement})
                rows = curs.fetchall()

        return [
            ReservationModelOut(
                id_reservation=r["id_reservation"],
                fk_utilisateur=r["fk_utilisateur"],
                fk_evenement=r["fk_evenement"],
                bus_aller=r["bus_aller"],
                bus_retour=r["bus_retour"],
                adherent=r["adherent"],
                sam=r["sam"],
                boisson=r["boisson"],
                date_reservation=r["date_reservation"],
            )
            for r in rows
        ]

    def find_by_id(self, id_reservation: int) -> Optional[ReservationModelOut]:
        """
        Récupère une réservation par son ID.
        """
        query = """
            SELECT id_reservation,
                   fk_utilisateur,
                   fk_evenement,
                   bus_aller,
                   bus_retour,
                   adherent,
                   sam,
                   boisson,
                   date_reservation
            FROM reservation
            WHERE id_reservation = %(id)s
        """
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_reservation})
                r = curs.fetchone()

        if not r:
            return None

        return ReservationModelOut(
            id_reservation=r["id_reservation"],
            fk_utilisateur=r["fk_utilisateur"],
            fk_evenement=r["fk_evenement"],
            bus_aller=r["bus_aller"],
            bus_retour=r["bus_retour"],
            adherent=r["adherent"],
            sam=r["sam"],
            boisson=r["boisson"],
            date_reservation=r["date_reservation"],
        )

    # ---------- CREATE ----------
    def create(self, reservation_in: ReservationModelIn) -> Optional[ReservationModelOut]:
        """
        Crée une nouvelle réservation.
        Contrainte d'unicité : UNIQUE(fk_utilisateur).
        """
        query = """
            INSERT INTO reservation (
                fk_utilisateur, fk_evenement,
                bus_aller, bus_retour,
                adherent, sam, boisson
            ) VALUES (
                %(fk_utilisateur)s, %(fk_evenement)s,
                %(bus_aller)s, %(bus_retour)s,
                %(adherent)s, %(sam)s, %(boisson)s
            )
            RETURNING id_reservation, date_reservation
        """
        params = {
            "fk_utilisateur": reservation_in.fk_utilisateur,
            "fk_evenement": reservation_in.fk_evenement,
            "bus_aller": reservation_in.bus_aller,
            "bus_retour": reservation_in.bus_retour,
            "adherent": reservation_in.adherent,
            "sam": reservation_in.sam,
            "boisson": reservation_in.boisson,
        }

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                try:
                    curs.execute(query, params)
                    row = curs.fetchone()
                    con.commit()
                except Exception as e:
                    con.rollback()
                    # Si vous utilisez psycopg2, vous pouvez tester e.pgcode == '23505' pour l'unicité
                    print(f"Erreur DAO lors de la création de la réservation : {e}")
                    return None

        return ReservationModelOut(
            id_reservation=row["id_reservation"],
            fk_utilisateur=reservation_in.fk_utilisateur,
            fk_evenement=reservation_in.fk_evenement,
            bus_aller=reservation_in.bus_aller,
            bus_retour=reservation_in.bus_retour,
            adherent=reservation_in.adherent,
            sam=reservation_in.sam,
            boisson=reservation_in.boisson,
            date_reservation=row["date_reservation"],
        )

    # ---------- UPDATE ----------
    def update_flags(
        self,
        id_reservation: int,
        *,
        bus_aller: Optional[bool] = None,
        bus_retour: Optional[bool] = None,
        adherent: Optional[bool] = None,
        sam: Optional[bool] = None,
        boisson: Optional[bool] = None,
    ) -> Optional[ReservationModelOut]:
        """
        Met à jour sélectivement les options de la réservation.
        """
        fields = []
        params = {"id": id_reservation}

        if bus_aller is not None:
            fields.append("bus_aller = %(bus_aller)s")
            params["bus_aller"] = bus_aller
        if bus_retour is not None:
            fields.append("bus_retour = %(bus_retour)s")
            params["bus_retour"] = bus_retour
        if adherent is not None:
            fields.append("adherent = %(adherent)s")
            params["adherent"] = adherent
        if sam is not None:
            fields.append("sam = %(sam)s")
            params["sam"] = sam
        if boisson is not None:
            fields.append("boisson = %(boisson)s")
            params["boisson"] = boisson

        if not fields:
            # Rien à mettre à jour
            return self.find_by_id(id_reservation)

        query = f"""
            WITH updated AS (
                UPDATE reservation
                SET {", ".join(fields)}
                WHERE id_reservation = %(id)s
                RETURNING id_reservation, fk_utilisateur, fk_evenement,
                          bus_aller, bus_retour, adherent, sam, boisson, date_reservation
            )
            SELECT * FROM updated
        """

        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, params)
                r = curs.fetchone()

        if not r:
            return None

        return ReservationModelOut(
            id_reservation=r["id_reservation"],
            fk_utilisateur=r["fk_utilisateur"],
            fk_evenement=r["fk_evenement"],
            bus_aller=r["bus_aller"],
            bus_retour=r["bus_retour"],
            adherent=r["adherent"],
            sam=r["sam"],
            boisson=r["boisson"],
            date_reservation=r["date_reservation"],
        )

    # ---------- DELETE ----------
    def delete(self, id_reservation: int) -> bool:
        """
        Supprime une réservation par ID.
        ON DELETE CASCADE sur les commentaires liés.
        """
        query = "DELETE FROM reservation WHERE id_reservation = %(id)s"
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_reservation})
                return curs.rowcount > 0

    # ---------- HELPERS / STATS ----------
    def count_by_event(self, id_evenement: int) -> int:
        """
        Retourne le nombre de réservations pour un événement.
        """
        query = "SELECT COUNT(*) AS c FROM reservation WHERE fk_evenement = %(id)s"
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_evenement})
                r = curs.fetchone()
                return int(r["c"]) if r else 0

    def exists_for_user(self, id_utilisateur: int) -> bool:
        """
        Indique si un utilisateur possède déjà une réservation
        (conforme à la contrainte UNIQUE(fk_utilisateur)).
        """
        query = "SELECT 1 FROM reservation WHERE fk_utilisateur = %(id)s LIMIT 1"
        with DBConnection().getConnexion() as con:
            with con.cursor() as curs:
                curs.execute(query, {"id": id_utilisateur})
                return curs.fetchone() is not None
