class CreneauBus:
    """ Définit un trajet de bus spécifique (aller ou retour) """
    def __init__(self, description: str, capacite: int):
        self.id_creneau_bus: Optional[int] = None # Géré par BDD 
        self.description = description
        self.capacite = capacite 

    def places_restantes(self) -> int:
        ...

    def est_complet(self) -> bool:
        return self.places_restantes() <= 0