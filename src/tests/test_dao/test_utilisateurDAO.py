import os

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
    utilisateur = UtilisateurDao().find_by_email(email)

    # THEN
    assert utilisateur is not None


def test_create():
    """ Création d'un utilisateur """

    # GIVEN
    utilisateur = UtilisateurModelIn(
        email=, prenom=, nom=,
        telephone=, administrateur=False,
        mot_de_passe=)

    # WHEN
    creation_ok = UtilisateurDao().create(utilisateur)

    # THEN
    assert creation_ok
    assert utilisateur.id_utilisateur


def test_update():
    """Met à jour un utilisateur"""

    # GIVEN
    new_numero_tel = "0612345678"
    utilisateur = Utilisateur(mail="test@exemple.fr", prenom="Khalid", nom="Jerrari",
                              numero_tel=new_numero_tel)

    # WHEN
    modification_ok = UtilisateurDao().update(utilisateur)

    # THEN
    assert modification_ok


def test_delete():
    """ Supprime un utilisateur """

    # GIVEN
    utilisateur = Utilisateur(id_utilisateur=123, mail="test@exemple.fr", prenom="Khalid",
                              nom="Jerrari", numero_tel="0678912345")

    # WHEN
    suppression_ok = UtilisateurDao().supprimer(utilisateur)

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
