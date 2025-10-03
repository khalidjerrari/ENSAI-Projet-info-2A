from datetime import datetime


class Evenement:
    """
    Classe représentant un événement.

    Attributs de classe :
    ---------------------
    _id_counter : int
        Compteur statique pour attribuer un identifiant unique à chaque événement.

    Attributs d'instance :
    ----------------------
    id_event : int
        Identifiant unique de l'événement, auto-incrémenté.
    creerPar : objet
        Objet représentant l'administrateur qui a créé l'événement.
    date_creation : datetime
        Date et heure de création de l'événement.
    titre : str
        Titre de l'événement.
    description : str
        Description détaillée de l'événement.
    categorie : str
        Catégorie à laquelle appartient l'événement.
    statut : str
        Statut actuel de l'événement (ex : ouvert, fermé).
    capacite : int
        Capacité maximale de participants.
    prixBase : float
        Prix de base pour l'événement.
    prixSam : float
        Prix spécial pour les samedis (ou autre tarif spécifique).
    prixAdherent : float
        Prix réduit pour les adhérents.

    Méthodes :
    ----------
    __init__(self, titre, description, categorie, statut, capacite, prixBase, prixSam, prixAdherent, creerPar)
        Initialise un nouvel événement avec les informations données.
    """

    _id_counter = 1  # variable de classe pour auto-incrémentation

    def __init__(self, titre, description, categorie, statut, capacite,
                 prixBase, prixSam, prixAdherent, creerPar):
        """
        Initialise un événement avec un ID unique, l'administrateur créateur, 
        la date de création et les autres détails fournis.

        Parameters:
        -----------
        titre : str
            Le titre de l'événement.
        description : str
            Description détaillée de l'événement.
        categorie : str
            La catégorie de l'événement.
        statut : str
            Statut actuel de l'événement (ex : ouvert, fermé).
        capacite : int
            Capacité maximale de participants.
        prixBase : float
            Prix de base de l'événement.
        prixSam : float
            Prix spécial pour les samedis (ou autre tarif spécifique).
        prixAdherent : float
            Prix réduit pour les adhérents.
        creerPar : objet
            L'administrateur qui a créé l'événement.
        """
        self.id_event = Evenement._id_counter
        Evenement._id_counter += 1

        self.creerPar = creerPar
        self.date_creation = datetime.now()

        self.titre = titre
        self.description = description
        self.categorie = categorie
        self.statut = statut
        self.capacite = capacite
        self.prixBase = prixBase
        self.prixSam = prixSam
        self.prixAdherent = prixAdherent
