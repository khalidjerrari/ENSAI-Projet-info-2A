# view/consulter/consulter_vue.py
from typing import Optional, Any, List
from datetime import date
from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from service.consultation_evenement_service import ConsultationEvenementService  # ✅ nouveau
from view.reservations.reservation_vue import ReservationVue


class ConsulterVue(VueAbstraite):
    """
    Vue pour la consultation des événements disponibles.
    Permet de lister, filtrer, rechercher et consulter les événements.
    Utilise ConsultationEvenementService (et non plus le DAO direct).
    """

    def __init__(self) -> None:
        super().__init__("CONSULTER")
        self.service = ConsultationEvenementService()  # ✅ on passe par le service

    def afficher(self) -> None:
        super().afficher()

    def choisir_menu(self) -> Optional[VueAbstraite]:
        # Import local pour éviter boucles circulaires
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
            "Lister les événements disponibles (avec places restantes)": "places",
            "Lister tous les événements": "tous",
            "Rechercher (ville, statut, dates)": "recherche",
            "Retour": "retour",
        }

        choix_action = inquirer.select(
            message="Que souhaitez-vous faire ?",
            choices=list(menu_choix.keys()),
        ).execute()

        action = menu_choix[choix_action]
        if action == "retour":
            return vue_de_retour("Retour au menu principal")

        events: List[Any] = []

        try:
            # ---------- 1. Récupération selon action ----------
            if action == "places":
                events = self.service.lister_avec_places_restantes(
                    limit=50,
                    a_partir_du=date.today()
                )

            elif action == "tous":
                events = self.service.lister_tous(limit=50)

            elif action == "recherche":
                ville = input("Ville (laisser vide pour ignorer) : ").strip() or None
                categorie = input("Catégorie (laisser vide) : ").strip() or None
                statut = input("Statut (ex: 'disponible en ligne', laisser vide) : ").strip() or None
                date_min = input("Date minimum (YYYY-MM-DD, vide pour ignorer) : ").strip()
                date_max = input("Date maximum (YYYY-MM-DD, vide pour ignorer) : ").strip()
                date_min = date.fromisoformat(date_min) if date_min else None
                date_max = date.fromisoformat(date_max) if date_max else None

                events = self.service.rechercher(
                    ville=ville,
                    categorie=categorie,
                    statut=statut,
                    date_min=date_min,
                    date_max=date_max,
                    limit=50
                )

            # ---------- 2. Vérification ----------
            if not events:
                print("\nAucun événement ne correspond à votre recherche.")
                input("\n(Entrée) pour continuer...")
                return self

            # ---------- 3. Formatage pour affichage ----------
            choices_events = []
            for ev in events:
                if isinstance(ev, dict):  # Cas de lister_avec_places_restantes()
                    places_val = ev.get("places_restantes")
                    places_str = f"({places_val} places)" if places_val is not None else ""
                    date_evt = ev.get("date_evenement", "")
                    titre = ev.get("titre", "N/A")
                else:  # Cas d’un EvenementModelOut
                    places_str = ""
                    date_evt = ev.date_evenement
                    titre = ev.titre

                titre_affiche = f"{date_evt} | {titre} {places_str}"
                choices_events.append({"name": titre_affiche, "value": ev})

            choices_events.append({"name": "--- Retour ---", "value": None})

            # ---------- 4. Sélection utilisateur ----------
            event_selectionne = inquirer.select(
                message="Sélectionnez un événement pour voir les détails et réserver :",
                choices=choices_events,
            ).execute()

            if event_selectionne is None:
                return self

            # Redirection vers la vue de réservation
            return ReservationVue(evenement=event_selectionne)

        except Exception as e:
            print(f"⚠️ Erreur lors de la récupération des événements : {e}")
            input("(Entrée) pour continuer...")
            return self
