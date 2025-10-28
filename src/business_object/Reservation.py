from __future__ import annotations
from datetime import datetime
from typing import Optional

# Import des types (pas d'import circulaire)
if typing.TYPE_CHECKING:
    from utilisateur import Utilisateur
    from evenement import Evenement
    from creneaubus import CreneauBus

class Reservation:
    """ Représente une inscription à un événement """
    def __init__(self, cree_par: Utilisateur, code_reservation: str, 
                 email_contact: str, prenom_contact: str, nom_contact: str, 
                 numero_tel: str, boit: bool, creneau_aller: CreneauBus, 
                 creneau_retour: CreneauBus, sam: bool, adherent: bool,
                 evenement_associe: Evenement):
                 
        self.id_reservation: Optional[int] = None
        self.cree_par = cree_par             
        self.code_reservation = code_reservation
        self.email_contact = email_contact       
        self.prenom_contact = prenom_contact  
        self.nom_contact = nom_contact        
        self.numero_tel = numero_tel             
        self.sam = sam                            
        self.adherent = adherent                 
        self.boit = boit              
        self.date_creation: datetime = datetime.now()
        self.creneau_aller = creneau_aller
        self.creneau_retour = creneau_retour
        self.evenement_associe = evenement_associe

    def calculer_prix(self) -> float:
        """
        Calcule le prix final de la réservation.
        
        Returns
        -------
            float
                Le prix calculé.
        """
        evt = self.evenement_associe
        
        # Si SAM, le prix est spécifique
        if self.sam:
            return evt.prix_sam
        
        prix = evt.prix_base
        
        # Si adhérent, on applique le tarif adhérent
        # (Hypothèse : prixAdherent est une *réduction*)
        if self.adherent:
            prix -= evt.prix_adherent
            
        # if self.boit:
        #    prix += evt.prix_boisson # Attribut à ajouter à Evenement
            
        return max(prix, 0) # Assurer que le prix n'est pas négatif