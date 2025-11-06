# src/view/reservations/reservation_vue.py
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator

from view.vue_abstraite import VueAbstraite
from view.session import Session
from dao.ReservationDAO import ReservationDao
from model.reservation_models import ReservationModelIn

class ReservationVue(VueAbstraite):
    """
    Vue pour la confirmation d'une réservation.
    """
    def __init__(self, evenement: dict, message=""):
        super().__init__(message)
        self.user = Session().utilisateur
        self.dao = ReservationDao()
        self.evenement = evenement
        self.fk_transport = evenement.get("fk_transport") # On récupère l'ID du transport

    def afficher(self):
        super().afficher()
        
        if not self.evenement or not self.fk_transport:
            print("Erreur : Aucun événement ou transport sélectionné.")
            return

        print(f"--- ✅ Confirmer la réservation ---")
        print(f"Événement : {self.evenement.get('titre')}")
        print(f"Date      : {self.evenement.get('date_evenement')}")
        print(f"Lieu      : {self.evenement.get('ville') or self.evenement.get('adresse') or 'N/A'}")


    def choisir_menu(self):
        # On importe ici pour éviter les boucles
        from view.client.connexion_client_vue import ConnexionClientVue
        
        if not self.user or not self.fk_transport:
            return ConnexionClientVue("Erreur lors de la réservation.")

        # On pose les questions "Sam? Boisson?" etc.
        try:
            questions = [
                inquirer.confirm(message="Êtes-vous adhérent ?", default=False, amark="✓"),
                inquirer.confirm(message="Êtes-vous SAM ce soir ?", default=False, amark="✓"),
                inquirer.confirm(message="Prenez-vous une boisson ?", default=False, amark="✓"),
                inquirer.confirm(message="Confirmer la réservation ?", default=True, amark="✓")
            ]
            
            reponses = inquirer.prompt(questions)
            
            # Si l'utilisateur n'a pas confirmé
            if not reponses[3]:
                return ConnexionClientVue("Réservation annulée.")

            # 1. On crée l'objet "formulaire"
            reservation_in = ReservationModelIn(
                fk_utilisateur=self.user.id_utilisateur,
                fk_transport=self.fk_transport,
                adherent=reponses[0],
                sam=reponses[1],
                boisson=reponses[2]
            )

            # 2. On appelle le DAO pour créer la réservation
            nouvelle_reservation = self.dao.create(reservation_in)

            if nouvelle_reservation:
                msg = f"🎉 Réservation #{nouvelle_reservation.id_reservation} confirmée !"
            else:
                # L'erreur la plus probable est la contrainte UNIQUE
                # (l'utilisateur a déjà réservé ce trajet)
                msg = "❌ Échec. Vous avez peut-être déjà réservé ce trajet."

            return ConnexionClientVue(msg) # On retourne au menu client
        
        except Exception as e:
            print(f"Erreur inattendue : {e}")
            return ConnexionClientVue("Une erreur est survenue.")