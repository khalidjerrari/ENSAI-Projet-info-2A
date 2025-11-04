# dao/reservation_dao.py
from typing import List
from dao.connection_manager import ConnectionManager
from models.reservation_models import ReservationModelOut


class ReservationDAO:
    """
    DAO pour la gestion des réservations (table 'reservation')
    """

    def find_by_user(self, id_utilisateur: int) -> List[ReservationModelOut]:
        """
        Récupère toutes les réservations faites par un utilisateur donné.

        Args:
            id_utilisateur (int): identifiant de l'utilisateur

        Returns:
            List[ReservationModelOut]: liste des réservations de cet utilisateur
        """
        query = (
            "SELECT r.id_reservation, "
            "       r.fk_utilisateur, "
            "       r.fk_transport, "
            "       r.adherent, "
            "       r.sam, "
            "       r.boisson, "
            "       r.date_reservation "
            "FROM reservation r "
            "JOIN utilisateur u ON r.fk_utilisateur = u.id_utilisateur "
            "WHERE r.fk_utilisateur = %s "
            "ORDER BY r.date_reservation DESC"
        )

        with ConnectionManager().getConnexion() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (id_utilisateur,))
                results = cursor.fetchall()

        reservations = []
        for res in results:
            reservations.append(
                ReservationModelOut(
                    id_reservation=res["id_reservation"],
                    fk_utilisateur=res["fk_utilisateur"],
                    fk_transport=res["fk_transport"],
                    adherent=res["adherent"],
                    sam=res["sam"],
                    boisson=res["boisson"],
                    date_reservation=res["date_reservation"],
                )
            )
        return reservations
