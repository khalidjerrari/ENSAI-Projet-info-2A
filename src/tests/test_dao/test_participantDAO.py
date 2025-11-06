import os
import uuid
from datetime import datetime

import pytest

from unittest.mock import patch

from utils.reset_database2 import ResetDatabase
from utils.securite import hash_password

from dao.ParticipantDAO import ParticipantDao
from model.participant_models import ParticipantModelOut, ParticipantModelIn


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test"""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


def test_find_all():
    """ Récupère la liste des participants """

    # GIVEN

    # WHEN
    participants = ParticipantDao().find_all()

    # THEN
    assert isinstance(participants, list)
    for j in participants:
        assert isinstance(j, ParticipantModelOut)
    assert len(participants) >= 2


def test_find_by_id():
    """Recherche par id d'un participant existant"""

    # GIVEN
    id_utilisateur = 3

    # WHEN
    participant = ParticipantDao().find_by_id(id_utilisateur)

    # THEN
    assert participant is not None


def test_find_by_email():
    """Recherche d'un participant par son email"""

    # GIVEN
    email = "alice.dupont@email.com"

    # WHEN
    participant = ParticipantDao().find_by_email(email)

    # THEN
    assert participant is not None


def test_create():
    """ Création d'un participant """

    # GIVEN
    email = f"julie.durand.{uuid.uuid4().hex[:8]}@email.com"
    participant = ParticipantModelIn(nom="Durand", prenom="Julie", telephone="0660066006",
                                     email=email,
                                     mot_de_passe="$2b$12$8H8eLcG1RXpzPvPtksm.debZkvArykH1trBf76pLM9KC3d8Tm3f82")

    # WHEN
    creation_ok = ParticipantDao().create(participant)

    # THEN
    assert creation_ok
    participant_en_base = ParticipantDao().find_by_email(email)
    assert participant_en_base is not None
    assert participant_en_base.prenom == "Julie"


def test_update():
    """Met à jour un utilisateur"""

    # GIVEN
    new_mail = "alice.dupont@gmail.com"
    participant = ParticipantModelOut(id_utilisateur=1, email=new_mail, prenom="Alice",
                                      nom="Dupont", telephone="0612345678",
                                      mot_de_passe="",
                                      administrateur=False, date_creation=datetime.now())

    # WHEN
    modification_ok = ParticipantDao().update(participant)

    # THEN
    assert modification_ok


def test_delete():
    """ Supprime un utilisateur """

    # GIVEN
    dao = ParticipantDao()
    participant = dao.find_by_id(5)
    assert participant is not None

    # WHEN
    suppression_ok = ParticipantDao().delete(participant.id_utilisateur)

    # THEN
    assert suppression_ok
