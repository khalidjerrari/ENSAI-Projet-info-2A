import os
import sys

# Ajoute automatiquement le dossier parent (src/) au PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import logging
import dotenv

from unittest import mock

from utils.log_decorator import log
from utils.singleton import Singleton
from dao.db_connection import DBConnection

#from service.joueur_service import JoueurService


class ResetDatabase(metaclass=Singleton):
    """
    Reinitialisation de la base de données
    """

    @log
    def lancer(self, test_dao=False):
        """Lancement de la réinitialisation des données
        Si test_dao = True : réinitialisation des données de test"""
        if test_dao:
            mock.patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}).start()
            pop_data_path = "data/pop_db_test.sql"
        else:
            os.environ["POSTGRES_SCHEMA"] = "projet_dao"
            pop_data_path = "data/pop_db.sql"

        dotenv.load_dotenv()

        schema = os.environ["POSTGRES_SCHEMA"]
        print(schema)

        create_schema = f"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};"

        init_db = open("data/init_db.sql", encoding="utf-8")
        init_db_as_string = init_db.read()
        init_db.close()

        pop_db = open(pop_data_path, encoding="utf-8")
        pop_db_as_string = pop_db.read()
        pop_db.close()

        try:
            with DBConnection().connection as connection:
                with connection.cursor() as cursor:
                    print(connection)
                    # if test_dao:
                        # print(create_schema)
                        # print(init_db_as_string)
                        # print(pop_db_as_string)
                    cursor.execute(create_schema)
                    cursor.execute(init_db_as_string)
                    cursor.execute(pop_db_as_string)
                del connection
                print("Done")
        except Exception as e:
            logging.info(e)
            raise

        # # Appliquer le hashage des mots de passe à chaque joueur
        # joueur_service = JoueurService()
        # for j in joueur_service.lister_tous(inclure_mdp=True):
        #     joueur_service.modifier(j)

        # return True


if __name__ == "__main__":
    ResetDatabase().lancer(False)
    ResetDatabase().lancer(True)
