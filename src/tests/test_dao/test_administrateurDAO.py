import os
import uuid
from datetime import datetime

import pytest

from unittest.mock import patch

from utils.reset_database import ResetDatabase
from utils.securite import hash_password

from dao.administrateur_dao import AdministrateurDao
from model.utilisateur_models import AdministrateurModelIn, AdministrateurModelOut


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
    admins = AdministrateurDao().find_all()

    # THEN
    assert isinstance(admins, list)
    for j in admins:
        assert isinstance(j, AdministrateurModelOut)
    # assert len(admins) >= 2 (y en a qu'un admin dans la base de test pour le moment)


def test_find_by_id():
    """Recherche par id d'un participant existant"""

    # GIVEN
    id_utilisateur = 2

    # WHEN
    admin = AdministrateurDao().find_by_id(id_utilisateur)

    # THEN
    assert admin is not None


def test_find_by_email():
    """Recherche d'un administrateur par son email"""

    # GIVEN
    email = "bob.martin@email.com"

    # WHEN
    admin = AdministrateurDao().find_by_email(email)

    # THEN
    assert admin is not None


def test_create():
    """ Création d'un administrateur """

    # GIVEN
    email = f"pierre.dubois.{uuid.uuid4().hex[:8]}@email.com"
    admin = AdministrateurModelIn(nom="Dubois", prenom="Pierre", telephone="0780982341",
                                  email=email,
                                  mot_de_passe="$2b$12$1cUPWY49/6B1QC7HaqlbIucbjyZ69qtje6xf6qTUITDphg1UEoWjK")

    # WHEN
    creation_ok = AdministrateurDao().create(admin)

    # THEN
    assert creation_ok
    admin_en_base = AdministrateurDao().find_by_email(email)
    assert admin_en_base is not None
    assert admin_en_base.prenom == "Pierre"


def test_update():
    """Met à jour un utilisateur"""

    # GIVEN
    new_mail = "bob.martin@gmail.com"
    admin = AdministrateurModelOut(id_utilisateur=2, email=new_mail, prenom="Bob",
                                   nom="Martin", telephone="0605060708",
                                   mot_de_passe="$2b$12$ZI9goAGUifVgF7dcZbNvgOjKED/Bfo193c5BDQW5RSaNxvkqu9QYa",
                                   administrateur=True, date_creation=datetime.now())

    # WHEN
    modification_ok = AdministrateurDao().update(admin)

    # THEN
    assert modification_ok


def test_delete():
    """ Supprime un utilisateur """

    # GIVEN
    dao = AdministrateurDao()
    admin = dao.find_by_id(5)
    assert admin is not None

    # WHEN
    suppression_ok = AdministrateurDao().delete(admin.id_utilisateur)

    # THEN
    assert suppression_ok
