import os
import logging
import dotenv
from unittest import mock

from utils.log_decorator import log
from utils.singleton import Singleton
from dao.db_connection import DBConnection


class ResetDatabase(metaclass=Singleton):
    """
    Réinitialisation de la base de données
    """

    @log
    def lancer(self, test_dao=False):
        """Lancement de la réinitialisation des données
        Si test_dao = True : réinitialisation des données de test"""

        dotenv.load_dotenv()

        if test_dao:
            schema = "projet_test_dao"
            pop_data_path = "data/pop_db_test.sql"
        else:
            schema = "projet_dao"
            pop_data_path = "data/pop_db.sql"

        # On utilise un patch temporaire du dictionnaire os.environ
        with mock.patch.dict(os.environ, {"POSTGRES_SCHEMA": schema}):
            self._reset_schema(schema, pop_data_path)

    def _reset_schema(self, schema, pop_data_path):
        """Exécute le drop / create du schéma et les scripts SQL"""
        print(f" Initialisation du schéma : {schema}")

        create_schema = f"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};"

        with open("data/init_db.sql", encoding="utf-8") as f:
            init_db_as_string = f.read()
        with open(pop_data_path, encoding="utf-8") as f:
            pop_db_as_string = f.read()

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    # Forcer le search_path vers le bon schéma
                    cursor.execute(create_schema)
                    cursor.execute(f"SET search_path TO {schema};")

                    cursor.execute(init_db_as_string)
                    cursor.execute(pop_db_as_string)

            print(f"Schéma {schema} réinitialisé avec succès !\n")
        except Exception as e:
            logging.exception(f"Erreur lors de la réinitialisation du schéma {schema} :")
            raise


if __name__ == "__main__":
    resetter = ResetDatabase()
    resetter.lancer(False)  # Schéma principal : projet_dao
    resetter.lancer(True)   # Schéma de test : projet_test_dao
