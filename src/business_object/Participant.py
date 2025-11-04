from Utilisateur import Utilisateur


class Participant(Utilisateur):
    """
    Classe modélisant un participant

    Attributs d'instance:
    --------------------
    id_utilisateur : int
        Permet d'identifier l'utilisateur, qui ici af=git en tant que participant
    emal : str
        Mail du participant
    prenom : str
        Prenom du participant
    nom : str
        Nom de famille du participant
    numeroTel : str
        Numéro de téléphone du participant
    mot_de_passe : hash ?
        Mot de passe hashé du participant pour qu'il puisse se connecter
    niveau_acces : ?
    """
    def __init__(self, id_utilisateur, email, prenom, nom, numeroTel, mot_de_passe, niveau_acces):
        super().__init__(self, id_utilisateur, email, prenom, nom, numeroTel, mot_de_passe,
                         niveau_acces)
