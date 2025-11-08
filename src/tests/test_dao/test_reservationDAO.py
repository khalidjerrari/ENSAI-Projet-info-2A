import os
from datetime import datetime


import pytest

from unittest.mock import patch

from utils.reset_database import ResetDatabase

from dao.reservation_dao import ReservationDao
from dao.evenement_dao import EvenementDao
from model.reservation_models import ReservationModelIn, ReservationModelOut


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test"""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


def test_find_by_user():
    """ Récupère la liste des réservations faites par un utilisateur donné"""

    # GIVEN
    fk_utilisateur = 1 

    # WHEN
    reservations = ReservationDao().find_by_user(fk_utilisateur)

    # THEN
    assert isinstance(reservations, list)
    for j in reservations:
        assert isinstance(j, ReservationModelOut)
    # assert len(reservations) >= 2 Il y a qu'une seule réservation pour l'utilisateur 1


def test_find_by_event():
    """Récupère les réservations faites pour un événement donné """
# Mohamed tu peux faire cette fonction si tu veux essayer


def test_find_by_id():
    """Récupère la réservation par son identifiant"""

    # GIVEN
    id_reservation = 3

    # WHEN
    reservation = ReservationDao().find_by_id(id_reservation)

    # THEN
    assert reservation is not None


def test_create():
    """ Création d'une réservation """

    # GIVEN
    reservation = ReservationModelIn(fk_utilisateur=1, fk_evenement=4, bus_aller=True,
                                     bus_retour=True, adherent=False, sam=False, boisson=True)

    # WHEN
    creation_ok = ReservationDao().create(reservation)

    # THEN
    assert creation_ok is not None, "La création de la réservation a échoué"
    assert creation_ok.fk_utilisateur == 1
    assert creation_ok.fk_evenement == 4


def test_update_flags():
    """Met à jour les flags d'une réservation"""

    # GIVEN
    id_reservation = 5
    new_bus_retour = False

    # WHEN
    reservation_updated = ReservationDao().update_flags(
        id_reservation=id_reservation,
        bus_retour=new_bus_retour,
        bus_aller=True,
        adherent=False,
        sam=False,
        boisson=True
    )

    # THEN
    assert reservation_updated is not None, "La réservation devrait exister"
    assert reservation_updated.bus_retour == new_bus_retour


def test_delete():
    """ Supprime une réservation """

    # GIVEN
    dao = ReservationDao()
    reservation = dao.find_by_id(3)
    assert reservation is not None

    # WHEN
    suppression_ok = EvenementDao().delete(reservation.id_reservation)

    # THEN
    assert suppression_ok
