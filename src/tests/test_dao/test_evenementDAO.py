import os
from datetime import datetime

import pytest

from unittest.mock import patch

from utils.reset_database2 import ResetDatabase

from dao.EvenementDAO import EvenementDao
from model.evenement_models import EvenementModelIn, EvenementModelOut


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
        assert isinstance(j, EvenementModelOut)
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
    """ Création d'un événement """

    # GIVEN
    evenement = EvenementModelIn(fk_transport=1, titre="Sortie Escalade", adresse="2 rue de l'Hôtel Dieu", ville="Rennes",
                                 date_evenement="2026-01-26", description="Initiation à l'escalade",
                                 capacite=20, categorie="Sport", statut="pas encore finalisé")

    # WHEN
    creation_ok = EvenementDao().create(evenement)

    # THEN
    assert creation_ok


def test_update():
    """Met à jour un utilisateur"""

    # GIVEN
    new_transport = 2
    evenement = EvenementModelOut(id_evenement=5, fk_transport=new_transport, titre="Sortie Escalade", adresse="2 rue de l'Hôtel Dieu", ville="Rennes",
                                 date_evenement="2026-01-26", description="Initiation à l'escalade",
                                 capacite=20, categorie="Sport", statut="pas encore finalisé", date_creation=datetime.now())

    # WHEN
    modification_ok = EvenementDao().update(evenement)

    # THEN
    assert modification_ok


def test_delete():
    """ Supprime un utilisateur """

    # GIVEN
    dao = EvenementDao()
    evenement = dao.find_by_id(3)
    assert evenement is not None

    # WHEN
    suppression_ok = EvenementDao().delete(evenement.id_evenement)

    # THEN
    assert suppression_ok
