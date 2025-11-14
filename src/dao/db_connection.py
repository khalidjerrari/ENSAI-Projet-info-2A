import os
import dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

from utils.singleton import Singleton


class DBConnection(metaclass=Singleton):
    """
    Classe gérant une unique connexion à la base PostgreSQL.
    Utilise le patron Singleton pour éviter plusieurs connexions simultanées.
    """

    def __init__(self):
        """Initialise la connexion à la base de données."""
        dotenv.load_dotenv()  # charge le fichier .env
        try:
            self.__connection = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST"),
                port=os.getenv("POSTGRES_PORT"),
                database=os.getenv("POSTGRES_DATABASE"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                options=f"-c search_path={os.getenv('POSTGRES_SCHEMA')}",
                cursor_factory=RealDictCursor,
            )
            print(f"Connexion réussie au schéma : {os.getenv('POSTGRES_SCHEMA')}")
        except Exception as e:
            print("Erreur de connexion à la base de données :", e)
            raise

    @property
    def connection(self):
        """Retourne la connexion PostgreSQL active."""
        return self.__connection

    def getConnexion(self):
        """Alias pour compatibilité."""
        return self.__connection
