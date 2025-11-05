# view/consulter/consulter_vue.py
from typing import Optional
from view.vue_abstraite import VueAbstraite
from view.accueil.accueil_vue import AccueilVue
from dao.Consultation_evenementDAO import ConsultationEvenementDao
from datetime import date


class ConsulterVue(VueAbstraite):
    def __init__(self) -> None:
        super().__init__("CONSULTER")
        self.dao = ConsultationEvenementDao()

    def afficher(self) -> None:
        super().afficher()  # nettoie + affiche le titre/message
        print("1) Lister tous les événements")
        print("2) Evénements disponibles (à partir d’aujourd’hui)")
        print("3) Recherche (ville / statut / dates)")
        print("4) Liste avec places restantes")
        print("0) Retour au menu principal")

    def choisir_menu(self) -> Optional[VueAbstraite]:
        choix = input("Votre choix : ").strip()
        if choix == "0":
            return AccueilVue("Retour au menu principal")

        elif choix == "1":
            events = self.dao.lister_tous(limit=50)
            self._afficher_events(events)
            input("\n(Entrée) pour continuer...")
            return self  # rester sur la même vue

        elif choix == "2":
            events = self.dao.lister_disponibles(limit=50, a_partir_du=date.today())
            self._afficher_events(events)
            input("\n(Entrée) pour continuer...")
            return self

        elif choix == "3":
            ville = input("Ville (laisser vide pour ignorer) : ").strip() or None
            statut = input("Statut (ex: 'disponible en ligne', laisser vide) : ").strip() or None
            dmin = input("Date min (YYYY-MM-DD, vide=ignorer) : ").strip() or None
            dmax = input("Date max (YYYY-MM-DD, vide=ignorer) : ").strip() or None
            date_min = date.fromisoformat(dmin) if dmin else None
            date_max = date.fromisoformat(dmax) if dmax else None
            events = self.dao.rechercher(ville=ville, statut=statut,
                                         date_min=date_min, date_max=date_max, limit=50)
            self._afficher_events(events)
            input("\n(Entrée) pour continuer...")
            return self

        elif choix == "4":
            rows = self.dao.lister_avec_places_restantes(limit=50, a_partir_du=date.today())
            for r in rows:
                print(f"- {r['date_evenement']} | {r['titre']} ({r.get('ville') or '-'}) "
                      f"— places restantes: {r['places_restantes']}")
            input("\n(Entrée) pour continuer...")
            return self  # ne pas retourner None

        else:
            print("Choix invalide.")
            input("\n(Entrée) pour continuer...")
            return self  # rester sur la vue

    def _afficher_events(self, events) -> None:
        if not events:
            print("(Aucun événement)")
            return
        for e in events:
            # s’adapte si e est un dict ou un objet
            date_evt = getattr(e, "date_evenement", None) or e.get("date_evenement")
            titre = getattr(e, "titre", None) or e.get("titre")
            ville = (getattr(e, "ville", None) or e.get("ville")) or "-"
            statut = getattr(e, "statut", None) or e.get("statut")
            print(f"- {date_evt} | {titre} ({ville}) — statut: {statut}")
