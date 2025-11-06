# view/consulter/consulter_vue.py
from typing import Optional
from InquirerPy import inquirer
from view.vue_abstraite import VueAbstraite
from dao.Consultation_evenementDAO import ConsultationEvenementDao
from view.reservations.reservation_vue import ReservationVue
from datetime import date


class ConsulterVue(VueAbstraite):
    def __init__(self) -> None:
        super().__init__("CONSULTER")
        self.dao = ConsultationEvenementDao()

    def afficher(self) -> None:
        super().afficher()

    def choisir_menu(self) -> Optional[VueAbstraite]:
        # On importe ici pour éviter les boucles circulaires
        from view.client.connexion_client_vue import ConnexionClientVue
        from view.accueil.accueil_vue import AccueilVue
        from view.session import Session
        
        user = Session().utilisateur
        
        if user:
            if getattr(user, "administrateur", False):
                from view.administrateur.connexion_admin_vue import ConnexionAdminVue 
                vue_de_retour = ConnexionAdminVue
            else:
                vue_de_retour = ConnexionClientVue
        else:
            vue_de_retour = AccueilVue
        
        menu_choix = {
            "Lister les événements disponibles (places restantes)": "places",
            "Lister tous les événements": "tous",
            "Rechercher (ville, statut, dates)": "recherche",
            "Retour": "retour"
        }

        choix_action = inquirer.select(
            message="Que souhaitez-vous faire ?",
            choices=list(menu_choix.keys()),
        ).execute()
        
        action = menu_choix[choix_action]
        
        if action == "retour":
            return vue_de_retour("Retour au menu principal")

        events: List[Any] = [] # Accepte n'importe quel type
        
        try:
            # --- 1. On récupère les événements (le code ne change pas) ---
            if action == "places":
                events = self.dao.lister_avec_places_restantes(limit=50, a_partir_du=date.today())
            
            elif action == "tous":
                events = self.dao.lister_tous(limit=50)
            
            elif action == "recherche":
                ville = input("Ville (laisser vide pour ignorer) : ").strip() or None
                statut = input("Statut (ex: 'disponible en ligne', laisser vide) : ").strip() or None
                events = self.dao.rechercher(ville=ville, statut=statut, limit=50)

            # --- 2. On vérifie si la liste est vide ---
            if not events:
                print("\n Aucun événement ne correspond à votre recherche.")
                input("\n(Entrée) pour continuer...")
                return self

            # --- 3. CORRECTION : On formate les événements ---
            choices_events = []
            for ev in events:
                
                # On vérifie si ev est un dictionnaire
                if isinstance(ev, dict):
                    # Cas 1: C'est un dict (de lister_avec_places_restantes)
                    places_val = ev.get('places_restantes')
                    places_str = f"({places_val} places)" if places_val is not None else ""
                    date_evt = ev.get('date_evenement', '')
                    titre = ev.get('titre', 'N/A')
                else:
                    # Cas 2: C'est un objet (EvenementModelOut)
                    places_str = "" # Pas de calcul de places ici
                    date_evt = ev.date_evenement
                    titre = ev.titre

                titre_affiche = f"{date_evt} | {titre} {places_str}"
                choices_events.append({"name": titre_affiche, "value": ev})

            choices_events.append({"name": "--- Retour ---", "value": None})

            # --- 4. On affiche le menu de sélection ---
            event_selectionne = inquirer.select(
                message="Sélectionnez un événement pour voir les détails et réserver :",
                choices=choices_events,
            ).execute()

            if event_selectionne is None:
                return self 

            return ReservationVue(evenement=event_selectionne)

        except Exception as e:
            print(f"Erreur lors de la récupération des événements : {e}")
            input("(Entrée) pour continuer...")
            return self
