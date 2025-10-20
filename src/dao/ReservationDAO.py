from typing import List
from dao.connection_manager import ConnectionManager
from models.reservation_models import ReservationModelOut


class ReservationDAO: 
    """
    Classe DAO pour la gestion des réservations
    """
    def find_by_user(self, id_user: int) -> List[ReservationModelOut]:
        """
        Récupère toutes les réservations filtrée avec l'identifiant de l'utilisateur

        Parameters:
        -----------

        Returns :
        ---------

        """
        query = (
            "SELECT r.id_reservation, r.id_user, r.aller, r.retour, r.boit, r.sam, r.adherent," 
            "r.date_reservation"
            "FROM reservation r"
            "JOIN utilisateur u ON r.id_user = u.id_user"
            "WHERE r.id_user = %s"
        )
        with ConnectionManager().getConnexion() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (id_user,))
                results = cursor.fetchall()
        
        reservations = []
        for res in results:
            resa = ReservationModelOut(
                id_reservation=res["id_reservation"],
                id_user=res["id_user"],
                aller=res["aller"],
                retour=res["retour"],
                boit=res["boit"],
                sam=res["sam"],
                adherent=res["adherent"],
                date_reservation=res["date_reservation"]
            )
            reservations.append(resa)
        return reservations
