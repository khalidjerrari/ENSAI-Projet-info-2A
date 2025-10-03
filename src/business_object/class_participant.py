from utilsateur import Utilisateur
class Participant(Utilisateur):
    def __init__(self, id_utilisateur, email, prenom, nom, numeroTel, mot_de_passe, niveau_acces):
        super().__init__(self, id_utilisateur, email, prenom, nom, numeroTel, mot_de_passe, niveau_acces)