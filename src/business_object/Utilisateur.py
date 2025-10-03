from abc import ABC


class Utilisateur(ABC):
    def __init__(self, email: str, prenom: str, nom: str, numeroTel : str, motDePasse: str) :
        self.email = email
        self.prenom = prenom
        self.nom = nom
        self.numeroTel = numeroTel
        self.motDePasse = motDePasse

    def consulterEvenementsOuverts(self):
        """
        Un utilisateur doit pouvoir consulter tous les événements mis en ligne
        
        Parameters
        ----------
            [...]
        
        Returns
        -------
            [...]
        """
        
    def listerReservations(self):
        """
        Un utilisateur a accès à toutes les réservations qu'il a réalisées

        Parameters
        ----------
            [...]
        
        Returns 
        -------
            [...]
        """

    def reserver(self, event: Evenement, aller: CreneauBus, retour: CreneauBus, boit: bool, sam : bool, adherent : bool):
        """
        Un utilisateur doit pouvoir réserver une ou plusieurs places à un événement

        Parameters
        ----------
            [...]
        
        Returns
        -------
            [...]

        """
        
    def seDesinscrire(codeReservation : str):
    
    def modifierReservation(codeReservation : str, nouvelAller: CreneauBus, nouveauRetour: CreneauBus, boit : bool) : Reservation


