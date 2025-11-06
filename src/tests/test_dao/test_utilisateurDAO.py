import os
import uuid
from datetime import datetime

import pytest

from unittest.mock import patch

from utils.reset_database2 import ResetDatabase
from utils.securite import hash_password

from dao.UtilisateurDAO import UtilisateurDao
from business_object.Utilisateur import Utilisateur
from model.utilisateur_models import UtilisateurModelOut, UtilisateurModelIn


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Initialisation des données de test"""
    with patch.dict(os.environ, {"SCHEMA": "projet_test_dao"}):
        ResetDatabase().lancer(test_dao=True)
        yield


def test_find_all():
    """ Récupère la liste des utilisateurs """

    # GIVEN

    # WHEN
    utilisateurs = UtilisateurDao().find_all()

    # THEN
    assert isinstance(utilisateurs, list)
    for j in utilisateurs:
        assert isinstance(j, UtilisateurModelOut)
    assert len(utilisateurs) >= 2


def test_find_by_id():
    """Recherche par id d'un utilisateur existant"""

    # GIVEN
    id_utilisateur = 1

    # WHEN
    utilisateur = UtilisateurDao().find_by_id(id_utilisateur)

    # THEN
    assert utilisateur is not None


def test_find_by_email():
    """Recherche d'un utilisateur par son email"""

    # GIVEN
    email = "alice.dupont@email.com"

    # WHEN
    participant = UtilisateurDao().find_by_email(email)

    # THEN
    assert participant is not None


def test_create():
    """ Création d'un utilisateur """

    # GIVEN
    email = f"marie.martin.{uuid.uuid4().hex[:8]}@example.com"
    utilisateur = UtilisateurModelIn(
        email=email,
        prenom="Marie",
        nom="Martin",
        telephone="0612345678",
        mot_de_passe="$2b$12$xagP1GoNLUNNYm8WIAqVRO7Z3HAIrOLFKxwLDAnu5oak/fyWkknDi",
        administrateur=True
        )

    # WHEN
    creation_ok = UtilisateurDao().create(utilisateur)

    # THEN
    assert creation_ok
    utilisateur_en_base = UtilisateurDao().find_by_email(email)
    assert utilisateur_en_base is not None
    assert utilisateur_en_base.prenom == "Marie"


def test_update():
    """Met à jour un utilisateur"""

    # GIVEN
    new_mail = "alice.dupont@gmail.com"
    utilisateur = UtilisateurModelOut(id_utilisateur=1, email=new_mail, prenom="Alice",
                                      nom="Dupont", telephone="0612345678",
                                      mot_de_passe="$2b$12$xagP1GoNLUNNYm8WIAqVRO7Z3HAIrOLFKxwLDAnu5oak/fyWkknDi",
                                      administrateur=True, date_creation=datetime.now())

    # WHEN
    modification_ok = UtilisateurDao().update(utilisateur)

    # THEN
    assert modification_ok


def test_delete():
    """ Supprime un utilisateur """

    # GIVEN
    dao = UtilisateurDao()
    utilisateur = dao.find_by_id(5)
    assert utilisateur is not None

    # WHEN
    suppression_ok = UtilisateurDao().delete(utilisateur.id_utilisateur)

    # THEN
    assert suppression_ok


def test_authentificate():
    """ Permet à l'utilisateur de s'authentifier"""

    # GIVEN
    id_utilisateur = 678
    mdp = "Mdpexemple35"

    # WHEN
    utilisateur = UtilisateurDao().authentificate(id_utilisateur,
                                                  hash_password(mdp, id_utilisateur))

    # THEN
    assert isinstance(utilisateur, Utilisateur)
