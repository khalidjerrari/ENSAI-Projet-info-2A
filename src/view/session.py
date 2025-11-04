from datetime import datetime

from utils.singleton import Singleton


class Session(metaclass=Singleton):
    """Stocke les données liées à une session.
    Cela permet par exemple de connaitre le joueur connecté à tout moment
    depuis n'importe quelle classe.
    Sans cela, il faudrait transmettre ce joueur entre les différentes vues.
    """

    def __init__(self):
        """Création de la session"""
        self.joueur = None
        self.debut_connexion = None

    def connexion(self, joueur):
        """Enregistement des données en session"""
        self.joueur = joueur
        self.debut_connexion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def deconnexion(self):
        """Suppression des données de la session"""
        self.joueur = None
        self.debut_connexion = None

    def afficher(self) -> str:
        """Afficher les informations de connexion"""
        res = "Actuellement en session :\n"
        res += "-------------------------\n"
        for att in list(self.__dict__.items()):
            res += f"{att[0]} : {att[1]}\n"

        return res
