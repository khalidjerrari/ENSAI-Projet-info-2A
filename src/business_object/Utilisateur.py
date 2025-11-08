from abc import ABC, abstractmethod

from dao.evenement_dao import EvenementDao
from dao.reservation_dao import ReservationDao
from business_object.Evenement import Evenement
from business_object.CreneauBus import CreneauBus
from business_object.Reservation import Reservation

from utils.api_brevo import send_email_brevo


class Utilisateur(ABC):
    """
    Cette classe permet de définir et d'identifier un utilisateur, qu'il soit administrateur
    ou participant.
    """
    def __init__(self, email: str, prenom: str, nom: str, numeroTel: str, motDePasse: str):
        self.email = email
        self.prenom = prenom
        self.nom = nom
        self.numeroTel = numeroTel
        self.motDePasse = motDePasse

    def listerEvents(self):
        """
        Liste de tous les évènements quelque soit le status. On utilise ici la classe "EvenementDAO"
        car c'est elle qui fait le lien avec la base de données.

        Returns:
        -------
            liste_events : liste de tous les événements
        """
        eventDAO = EvenementDao()
        liste_events = eventDAO.find_all()
        return liste_events

    def consulterEvenementsOuverts(self):
        """
        Un utilisateur doit pouvoir consulter tous les événements mis en ligne

        Returns
        -------
            events_ouverts : liste d'évènements qui sont consultables en ligne
        """
        liste_events = self.listerEvents()
        events_ouverts = [e for e in liste_events if e.statut == "en_ligne"]
        return events_ouverts

    def reserver(self, event: Evenement, aller: CreneauBus, retour: CreneauBus,
                 boit: bool, sam: bool, adherent: bool) -> Reservation:
        """
        Un utilisateur doit pouvoir réserver une ou plusieurs places à un événement

        Parameters
        ----------
            event : un événement de la classe Evenement
            aller : horaire du bus pour aller à l'événement
            retour : horaire du bus pour le retour (qui part de l'événement)
            boit : booléen, qui indique si le participant boit ou pas
            sam : booléen, qui indique si le participant est sam : il vient avec sa voiture,
                ne boit pas d'alcool et ramène des personnes avec sa voiture.
            adhérent : booléen, qui indique si le participant est adhérent au BDE
            (change le prix de l'événement)

        Returns
        -------
            Reservation
                L'objet Reservation qui vient d'être créé et sauvegardé.
        """
        resDAO = ReservationDAO()

        # --- 1. Logique métier : Vérification des places ---
        if event.places_restantes() <= 0:
            raise Exception("Désolé, l'événement est complet.")
        if aller.places_restantes() <= 0:
            raise Exception(f"Désolé, le créneau '{aller.description}' est complet.")
        if retour.places_restantes() <= 0:
            raise Exception(f"Désolé, le créneau '{retour.description}' est complet.")

        # --- 2. Préparation : Création de l'objet Réservation ---
        code_genere = str(uuid.uuid4())[:8].upper()

        nouvelle_res = Reservation(
            cree_par=self,
            code_reservation=code_genere,
            email_contact=self.email,
            prenom_contact=self.prenom,
            nom_contact=self.nom,
            numero_tel=self.numero_tel,
            boit=boit,
            creneau_aller=aller,
            creneau_retour=retour,
            sam=sam,
            adherent=adherent,
            evenement_associe=event
        )
        # --- 3. Persistence : Sauvegarde via le DAO ---
        res_creee = resDAO.create(nouvelle_res)
        # --- 4. Post-action (ex: Email) ---
        subject = f"Confirmation de votre réservation pour {self.event}"
        message = (
            f"Bonjour {self.utilisateur.nom},\n\n"
            f"Votre réservation pour l'événement '{self.event}' a bien été confirmée.\n"
            "Merci de votre confiance et à très bientôt !\n\n"
            "— L’équipe du BDE Ensai"
            )

        status, response = send_email_brevo(self.utilisateur.email, subject, message)
        print("Email de confirmation envoyé :", status, response)

    def listerMesReservations(self):
        """
        Un utilisateur a accès à toutes les réservations qu'il a réalisées pour lui.

        Returns
        -------
            liste_resaDAO : liste des réservations faites par l'utilisateur
        """
        resaDAO = ReservationDAO()
        liste_resa = resaDAO.find_by_user()
        return liste_resa

    def seDesinscrire(self, codeReservation: str) -> None:
        """
        Un utilisateur doit pouvoir se désinscrire d'un événement quelque soit la raison.
        Cela entraînera une annulation de sa réservation.

        Parameters :
        ------------
            codeReservation : str
                Le code unique de la réservation à annuler.
        """
        resDAO = ReservationDAO()
        # --- 1. Vérification : Trouver la réservation ---
        resa = resDAO.find_by_code(self.codeReservation)
        if resa is None:
            raise Exception("Réservation non trouvée.")
        # --- 2. Logique métier : Vérifier les droits ---
        if resa.cree_par.id_utilisateur != self.id_utilisateur:
            raise Exception("Vous n'êtes pas autorisé à annuler cette réservation.")
        # --- 3. Persistence : Suppression via le DAO ---
        resDAO.delete(resa)
        # --- 4. Post-action (ex: Email) ---
        subject = f"Annulation de votre réservation pour {self.event}"
        message = (
            f"Bonjour {self.utilisateur.nom},\n\n"
            f"Votre réservation pour l'événement '{self.event}' a bien été annulée.\n"
            "Nous espérons vous revoir bientôt à un autre événement !\n\n"
            "— L’équipe du BDE Ensai"
            )

        status, response = send_email_brevo(self.utilisateur.email, subject, message)
        print("Email d’annulation envoyé :", status, response)

    @abstractmethod
    def modifierReservation(codeReservation: str, nouvelAller: CreneauBus,
                            nouveauRetour: CreneauBus, boit: bool):
        pass
