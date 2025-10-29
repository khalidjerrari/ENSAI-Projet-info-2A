    classDiagram
        direction LR


class Utilisateur {
    +id: int
    +email: str
    +prenom: str
    +nom: str
    -motDePasseHache: str
    +verifierMotDePasse(mdpClair: str): bool
}

    class Administrateur {
        -niveauAcces: int
        }


    class Participant {
        +etudiantId: str
        }


class Evenement {
    +id: int
    +titre: str
    +description: str
    +capaciteMax: int
    +ouvert: bool
    +prixBase: decimal
    +supplementBoisson: decimal
    +placesRestantes(): int
    +estComplet(): bool
    +ajouterCreneau(c: CreneauBus): void
    }

class DirectionBus {
  <<enum>>
    Aller
    Retour
  }

class CreneauBus {
    +id: int
    +direction: DirectionBus
    +depart: datetime
    +arrivee: datetime
    +lieuDepart: str
    +lieuArrivee: str
    +capacite: int
    +placesRestantes(): int
    +estComplet(): bool
  }

class StatutReservation {
  <<enum>>
    Creee
    Validee
    Annulee
  }

class Reservation {
    +code: str
    +emailContact: str
    +prenomContact: str
    +nomContact: str
    +boit: bool
    +prixTotal: decimal
    +statut: StatutReservation
    +dateCreation: datetime
    +annuler(): void
  }

class StatCreneau {
    +creneau: CreneauBus
    +inscrits: int
    +restants: int
    +tauxRemplissage: float
  }

class StatistiquesEvenement {
    +totalInscrits: int
    +restantsEvenement: int
    +statsParCreneau: List~StatCreneau~
  }

class ServiceCompte {
    +creerCompteAdmin(email, prenom, nom, mdpClair, niveauAcces=1): Administrateur
    +creerCompteParticipant(email, prenom, nom, mdpClair, etudiantId): Participant
    +authentifierUtilisateur(email, mdpClair): Utilisateur
  }

class ServiceEvenement {
    +creerEvenement(admin: Administrateur, titre, description, capaciteMax, prixBase, supBoisson): Evenement
    +fermerEvenement(e: Evenement): void
    +ajouterCreneau(e: Evenement, direction: DirectionBus, depart: datetime, arrivee: datetime, lieuDepart: str, lieuArrivee: str, capacite: int): CreneauBus
    +listerEvenementsOuverts(): List~Evenement~
    +inscrire(p: Participant, e: Evenement, aller: CreneauBus, retour: CreneauBus, boit: bool): Reservation
    +desinscrire(p: Participant, codeReservation: str): bool
    +modifierReservation(p: Participant, codeReservation: str, nouvelAller: CreneauBus, nouveauRetour: CreneauBus, boit: bool): Reservation
    +calculerStatistiques(e: Evenement): StatistiquesEvenement
    +listerInscrits(e: Evenement): List~Reservation~
    +supprimerReservation(code: str): bool
  }

class ServiceEmail {
    +envoyerConfirmation(res: Reservation, evt: Evenement): void
    +envoyerAnnulation(res: Reservation, evt: Evenement): void
  }

  %% Héritage
  Administrateur --|> Utilisateur
  Participant --|> Utilisateur

  %% Associations
  Evenement "1" o-- "0..*" CreneauBus : contient
  Reservation "*" --> "1" Participant : effectue
  Reservation "*" --> "1" Evenement : concerne
  Reservation "*" --> "1" CreneauBus : aller
  Reservation "*" --> "1" CreneauBus : retour

  ServiceEvenement ..> Evenement : crée/ferme
  ServiceEvenement ..> CreneauBus : propose
  ServiceEvenement ..> Reservation : gère
  ServiceEvenement ..> StatistiquesEvenement : produit
  ServiceCompte ..> Utilisateur : crée/authentifie
  ServiceEmail ..> Reservation
  ServiceEmail ..> Evenement
