from abc import ABC, abstractmethod
from Evenement import Evenement


class Utilisateur(ABC):
    def __init__(self, email: str, prenom: str, nom: str, numeroTel : str, motDePasse: str) :
        self.email = email
        self.prenom = prenom
        self.nom = nom
        self.numeroTel = numeroTel
        self.motDePasse = motDePasse

    def listerEvents(self) :
        """
        Liste de tous les évènements quelque soit le status
        
        Returns:
        -------
            liste_events : liste de tous les événements dont le statut est "en_ligne"
        """
        #listeEvents fait appel à listerEventsDAO qui elle sera une requête SQL (a mettre dans evenementS dao)

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
        liste_events = listerEvents(self)
        events_ouverts = [e for e in liste_events if event.statut == "en_ligne"] #Faire un tri pour que le statut soit "en_ligne". SQL?
        return events_ouverts
        
    def listerMesReservations(self):
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
    
    
    @abstractmethod
    def modifierReservation(codeReservation : str, nouvelAller: CreneauBus, nouveauRetour: CreneauBus, boit : bool) :



