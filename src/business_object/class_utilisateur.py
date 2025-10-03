from abc import ABC, abstractmethod
class Utilisateur(ABC):
    
    def __init__(self, id_utilisateur, email, prenom, nom, numeroTel, mot_de_passe, niveau_acces):
        self.id_utilisateur = id_utilisateur
        self.email = email
        self.prenom = prenom
        self.nom = nom
        self.numeroTel=numeroTel
        self.mot_de_passe=mot_de_passe
        self.niveau_acces=niveau_acces

    @abstractmethod
    def consulterEvenementOuverts(self):
        pass

    @abstractmethod
    def listerReservations(self):
        pass

    @abstractmethod
    def reserver(self):
        pass

    @abstractmethod
    def seDesinscrire(self):
        pass

    @abstractmethod
    def modifierReservation(self):
        pass

        