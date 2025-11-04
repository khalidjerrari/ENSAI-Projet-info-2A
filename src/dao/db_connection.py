import os
import dotenv
import psycopg2

from psycopg2.extras import RealDictCursor
from utils.singleton import Singleton


class DBConnection(metaclass=Singleton):
    """
    Classe de connexion à la base de données
    Elle permet de n'ouvrir qu'une seule et unique connexion
    """

    def __init__(self):
        """Ouverture de la connexion"""
        dotenv.load_dotenv()

        self.__connection = psycopg2.connect(
            host=os.environ["postgresql-66551.user-khalid76"],
            port=os.environ["9876"],
            database=os.environ["defaultdb"],
            user=os.environ["user-khalid76"],
            password=os.environ["9dyhflppaxy1jz0urk4e"],
            options=f"-c search_path={os.environ['POSTGRES_SCHEMA']}",
            cursor_factory=RealDictCursor,
        )

    @property
    def connection(self):
        return self.__connection
