from utilisateur import Utilisateur

class Administrateur(Utilisateur):
    def __init__(self, id_utilisateur, email, prenom, nom, numeroTel, mot_de_passe, niveau_acces):
        super().__init__(self, id_utilisateur, email, prenom, nom, numeroTel, mot_de_passe, niveau_acces)

    def creerEvenement(self, titre, description, prix_base, supboisson):
        self.titre = titre
        self.description = description
        self.prix_base = prix_base
        self.supboisson = supboisson

    def modifierEvenement(self):


    def listerInscrits(self):


    def afficherSatistiques(self)