# dao/reservation_dao.py
from dao.db_connection import DBConnection
from model.reservation_models import ReservationModelOut
from model.reservation_models import ReservationModelIn
from typing import List, Optional

class ReservationDao:
    """
    DAO pour la gestion des réservations (table 'reservation')
    """

    def find_by_user(self, id_utilisateur: int):
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

        with DBConnection().getConnexion() as connection:
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

    def create(self, reservation_in: ReservationModelIn) -> Optional[ReservationModelOut]:
        """
        Crée une nouvelle réservation dans la base de données.
        """
        
        query = (
            "INSERT INTO reservation (fk_utilisateur, fk_transport, adherent, sam, boisson) "
            "VALUES (%(fk_utilisateur)s, %(fk_transport)s, %(adherent)s, %(sam)s, %(boisson)s) "
            "RETURNING id_reservation, date_reservation"
        )
        
        params = {
            "fk_utilisateur": reservation_in.fk_utilisateur,
            "fk_transport": reservation_in.fk_transport,
            "adherent": reservation_in.adherent,
            "sam": reservation_in.sam,
            "boisson": reservation_in.boisson
        }

        with DBConnection().getConnexion() as connection:
            with connection.cursor(dictionary=True) as cursor:
                try:
                    cursor.execute(query, params)
                    row = cursor.fetchone() 
                    if row is None:
                        return None # L'insertion a échoué
                    
                    connection.commit()
                    
                    return ReservationModelOut(
                        id_reservation=row["id_reservation"],
                        date_reservation=row["date_reservation"],
                        fk_utilisateur=reservation_in.fk_utilisateur,
                        fk_transport=reservation_in.fk_transport,
                        adherent=reservation_in.adherent,
                        sam=reservation_in.sam,
                        boisson=reservation_in.boisson
                    )
                
                except Exception as e:
                    # Si la réservation existe déjà (contrainte unique), 
                    # ou autre erreur SQL.
                    connection.rollback() # On annule la transaction
                    print(f"Erreur DAO lors de la création de la réservation : {e}")
                    return None