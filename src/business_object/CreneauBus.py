class CreneauBus:
    """
    Classe représentant un créneau horaire de bus.

    Attributs :
        id_creneauBus (int) : Identifiant unique (géré par la base de données en SERIAL)
        description (str)   : Description du créneau (ex: "Départ 8h30 - Rennes > Paris")
        capacite (int)      : Nombre total de places disponibles dans ce créneau
        inscrits (int)      : Nombre actuel de réservations (géré côté logique métier)
    """

    def __init__(self, description: str, capacite: int):
        self.id_creneauBus: int | None = None   # sera affecté par la DB (SERIAL)
        self.description: str = description
        self.capacite: int = capacite
        self.inscrits: int = 0  # initialement aucune place réservée

    def placesRestantes(self) -> int:
        """
        Retourne le nombre de places encore disponibles.
        """
        return max(0, self.capacite - self.inscrits)

    def estComplet(self) -> bool:
        """
        Indique si le créneau est complet (plus de places disponibles).
        """
        return self.inscrits >= self.capacite

    def __str__(self) -> str:
        """
        Représentation textuelle utile pour l'affichage.
        """
        return (f"CreneauBus(id={self.id_creneauBus}, "
                f"description='{self.description}', "
                f"capacite={self.capacite}, "
                f"inscrits={self.inscrits}, "
                f"places_restantes={self.placesRestantes()})")
