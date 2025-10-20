from abc import ABC, abstractmethod
from EvenementDAO import EvenementDAO


class Utilisateur(ABC):
    def __init__(self, email: str, prenom: str, nom: str, numeroTel : str, motDePasse: str) :
        self.email = email
        self.prenom = prenom
        self.nom = nom
        self.numeroTel = numeroTel
        self.motDePasse = motDePasse

    def listerEvents(self) :
        """
        Liste de tous les évènements quelque soit le status. On utilise ici la classe "EvenementDAO"
        car c'est elle qui fait le lien avec la base de données. 
        
        Returns:
        -------
            liste_events : liste de tous les événements
        """
        eventDAO = EvenementDAO()
        liste_events = eventDAO.find_all(limit=limit, offset=offset)
        return liste_events

    def consulterEvenementsOuverts(self):
        """
        Un utilisateur doit pouvoir consulter tous les événements mis en ligne
        
        Returns
        -------
            events_ouverts : liste d'évènements qui sont consultables en ligne
        """
        liste_events = listerEvents(self)
        events_ouverts = [e for e in liste_events if eventDAO.statut == "en_ligne"]
        return events_ouverts

    def reserver(self, event: Evenement, aller: CreneauBus, retour: CreneauBus, boit: bool, sam : bool, adherent : bool):
        """
        Un utilisateur doit pouvoir réserver une ou plusieurs places à un événement

        Parameters
        ----------
            event : un événement de la classe Evenement
            aller : horaire du bus pour aller à l'événement
            retour : horaire du bus pour le retour (qui part de l'événement)
            boit : booléen, qui indique si le participant boit ou pas
            sam : booléen, qui indique si le participant est sam : il vient avec sa voiture, ne boit pas d'alcool et ramène des personnes avec
                    sa voiture.
            adhérent : booléen, qui indique si le participant est adhérent au BDE (change le prix de l'événement)
        
        Returns
        -------
            Rien

        """
    
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
        
    def seDesinscrire(codeReservation : str):
    
    
    @abstractmethod
    def modifierReservation(codeReservation : str, nouvelAller: CreneauBus, nouveauRetour: CreneauBus, boit : bool) :
        pass



