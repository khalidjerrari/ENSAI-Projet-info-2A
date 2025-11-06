# dao/reservation_dao.py
from dao.db_connection import DBConnection
from model.reservation_models import ReservationModelOut, ReservationModelIn
from typing import List, Optional

class ReservationDao:
    """
    DAO pour la gestion des réservations (table 'reservation')
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
            JOIN utilisateur u ON r.fk_utilisateur = u.id_utilisateur
            WHERE r.fk_utilisateur = %(id_utilisateur)s
            ORDER BY r.date_reservation DESC
        """

        with DBConnection().getConnexion() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute(query, {"id_utilisateur": id_utilisateur})
                results = cursor.fetchall()

        reservations = [
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
            for r in results
        ]

        return reservations

    # ---------- CREATE ----------
    def create(self, reservation_in: ReservationModelIn) -> Optional[ReservationModelOut]:
        """
        Crée une nouvelle réservation dans la base de données.
        Gère la contrainte UNIQUE(fk_utilisateur).
        """
        query = """
            INSERT INTO reservation (
                fk_utilisateur, fk_evenement,
                bus_aller, bus_retour,
                adherent, sam, boisson
            )
            VALUES (
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

        with DBConnection().getConnexion() as connection:
            with connection.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute(query, params)
                    row = cursor.fetchone()
                    connection.commit()

                    return ReservationModelOut(
                        id_reservation=row["id_reservation"],
                        date_reservation=row["date_reservation"],
                        fk_utilisateur=reservation_in.fk_utilisateur,
                        fk_evenement=reservation_in.fk_evenement,
                        bus_aller=reservation_in.bus_aller,
                        bus_retour=reservation_in.bus_retour,
                        adherent=reservation_in.adherent,
                        sam=reservation_in.sam,
                        boisson=reservation_in.boisson,
                    )

                except Exception as e:
                    connection.rollback()
                    print(f"Erreur DAO lors de la création de la réservation : {e}")
                    return None
