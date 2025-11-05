import os

import pytest

from unittest.mock import patch

from utils.reset_database import ResetDatabase
from utils.securite import hash_password

from dao.EvenementDAO import EvenementDao
from business_object.Evenement import Evenement


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test"""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


def test_find_all():
    """ Récupère la liste des événements"""

    # GIVEN

    # WHEN
    evenements = EvenementDao().find_all()

    # THEN
    assert isinstance(evenements, list)
    for j in evenements:
        assert isinstance(j, Evenement)
    assert len(evenements) >= 2


def test_find_by_id():
    """Récupère l'événement par l'identifiant """

    # GIVEN
    id_evenement = 1

    # WHEN
    evenement = EvenementDao().find_by_id(id_evenement)

    # THEN
    assert evenement is not None


def test_find_by_transport():
    """Récupère la liste des événements liés à un transport"""

    # GIVEN
    fk_transport = 4

    # WHEN
    evenements = EvenementDao().find_by_transport(fk_transport)

    # THEN
    assert evenements is not None


def test_create():
    """ Création d'un utilisateur """

    # GIVEN
    evenement = Evenement(titre="Salon de l’Art", adresse="5 Avenue de Nice", ville="Nice",
                          date_evenement="2025-12-01", description="Exposition d’art contemporain",
                          capacite=50, categorie="Art", statut="pas encore finalisé")

    # WHEN
    creation_ok = EvenementDao().create(evenement)

    # THEN
    assert creation_ok
    assert evenement.id_evenement
