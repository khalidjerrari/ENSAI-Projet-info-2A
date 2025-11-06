class CreneauBus:
    """
    Représente un créneau de bus (modèle métier).

    Champs alignés sur la table `bus` :
        - id_bus : int | None
        - fk_evenement : int | None
        - matricule : str | None
        - nombre_places : int (> 0)
        - direction : str ('aller' ou 'retour')
        - description : str (<= 100, obligatoire, unique côté BDD)

    Champs métier (non BDD) :
        - inscrits : int (nb de réservations calculé ailleurs)
    """

    ALLOWED_DIRECTIONS = {"aller", "retour"}

    def __init__(
        self,
        description: str,
        nombre_places: int,
        *,
        direction: str = "aller",
        fk_evenement: int | None = None,
        matricule: str | None = None,
        id_bus: int | None = None,
        inscrits: int = 0,
    ):
        # --- Identité & rattachement ---
        self.id_bus: int | None = id_bus
        self.fk_evenement: int | None = fk_evenement

        # --- Attributs principaux ---
        self.matricule: str | None = matricule
        self.description: str = description
        self.nombre_places: int = int(nombre_places)
        self.direction: str = direction

        # --- État métier ---
        self.inscrits: int = int(inscrits)

        # --- Validations légères (cohérentes avec la BDD) ---
        if not self.description or len(self.description) > 100:
            raise ValueError("description est requise (<= 100 caractères).")
        if self.nombre_places <= 0:
            raise ValueError("nombre_places doit être > 0.")
        if self.direction not in self.ALLOWED_DIRECTIONS:
            raise ValueError(f"direction doit être dans {self.ALLOWED_DIRECTIONS}.")
        if self.matricule and len(self.matricule) > 20:
            raise ValueError("matricule doit faire <= 20 caractères.")
        if self.inscrits < 0:
            raise ValueError("inscrits ne peut pas être négatif.")

    # ----------------------------
    # Logique métier
    # ----------------------------
    def placesRestantes(self) -> int:
        """Retourne le nombre de places encore disponibles (>= 0)."""
        return max(0, self.nombre_places - self.inscrits)

    def estComplet(self) -> bool:
        """Indique si le créneau est complet (plus de places disponibles)."""
        return self.inscrits >= self.nombre_places

    def set_inscrits(self, n: int) -> None:
        """Met à jour le nombre d'inscrits (contrôle la cohérence)."""
        n = int(n)
        if n < 0:
            raise ValueError("inscrits ne peut pas être négatif.")
        self.inscrits = n

    def __str__(self) -> str:
        return (
            "CreneauBus("
            f"id_bus={self.id_bus}, "
            f"fk_evenement={self.fk_evenement}, "
            f"matricule={repr(self.matricule)}, "
            f"direction='{self.direction}', "
            f"description='{self.description}', "
            f"nombre_places={self.nombre_places}, "
            f"inscrits={self.inscrits}, "
            f"places_restantes={self.placesRestantes()})"
        )
