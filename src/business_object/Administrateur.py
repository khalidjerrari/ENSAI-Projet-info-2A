from utilisateur import Utilisateur

class Administrateur(Utilisateur):
    def __init__(self, id_utilisateur, email, prenom, nom, numeroTel, mot_de_passe, niveau_acces):
        super().__init__(self, id_utilisateur, email, prenom, nom, numeroTel, mot_de_passe, niveau_acces)

    def creerEvenement(self, titre, description, prix_base, supboisson) -> Evenement:
        """
        Crée un nouvel événement dans le système.
        L'événement est créé en 'brouillon' par défaut.
        
        Parameters
        ----------
            titre : str
            description : str
            categorie : str
            capacite : int
            prix_base : float
            prix_sam : float
            prix_adherent : float
            
        Returns
        -------
            Evenement
                L'objet événement créé et sauvegardé en BDD.
        """
        evtDAO = EvenementDao()
        
        nouvel_evt = Evenement(
            cree_par=self,
            titre=titre,
            description=description,
            categorie=categorie,
            statut=StatutEvenement.BROUILLON, # Par défaut
            capacite=capacite,
            prix_base=prix_base,
            prix_sam=prix_sam,
            prix_adherent=prix_adherent
        )
        
        # Délégation de la création au DAO
        return evtDAO.create(nouvel_evt)

    def modifierEvenement(self, event: Evenement) -> None:
        """
        Met à jour un événement existant en base de données.

        Parameters
        ----------
            event : Evenement
                L'objet événement modifié (en mémoire) à persister en BDD.
        """
        print(f"ADMIN: Demande de modification BDD pour l'événement '{event.titre}'...")
        
        eventDAO = EvenementDao()
        # Le DAO se chargera d'exécuter la requête SQL "UPDATE evenement SET ..."
        eventDAO.update(event)
        print(f"ADMIN: Événement '{event.titre}' mis à jour avec succès.")

    def lister_inscrits(self, e: Evenement) -> List[Reservation]:
        """
        Liste tous les inscrits (réservations) pour un événement donné.
        
        Parameters
        ----------
            e : Evenement
                L'événement dont on veut la liste des inscrits.
                
        Returns
        -------
            List[Reservation]
                La liste des réservations pour cet événement.
        """
        resDAO = ReservationDao()
        return resDAO.find_by_event_id(e.id_evenement)


    def afficher_statistiques(self, event: Evenement) -> StatistiquesEvenement:
        """
        Calcule et retourne les statistiques agrégées pour un événement donné.

        Parameters
        ----------
            event : Evenement
                L'événement pour lequel calculer les statistiques.
        
        Returns
        -------
            StatistiquesEvenement
                Un objet contenant les statistiques.
        """
        print(f"ADMIN: Calcul des statistiques pour '{event.titre}'...")
        
        # On instancie les DAOs nécessaires pour récupérer les chiffres
        resDAO = ReservationDao()
        creneauDAO = CreneauBusDao() 

        # --- 1. Statistiques globales de l'événement ---
        
        # On demande au DAO de compter le total des inscrits
        total_inscrits = resDAO.get_count_for_event(event.id_evenement)
        
        # Le nombre de places restantes
        restants_evenement = event.capacite - total_inscrits

        # --- 2. Statistiques par créneau de bus ---
        stats_par_creneau_list: List[StatCreneauBus] = []
        
        # On boucle sur les créneaux qui sont liés à l'événement
        # (On suppose que event.creneaux_bus a été chargé depuis la BDD)
        if event.creneaux_bus:
            for creneau in event.creneaux_bus:
                
                # On demande au DAO le compte pour CE créneau
                inscrits_creneau = creneauDAO.get_reservation_count(creneau.id_creneau_bus)
                
                # On calcule les places restantes pour le créneau
                restants_creneau = creneau.capacite - inscrits_creneau
                
                # On calcule le taux de remplissage
                taux_remplissage = 0.0
                if creneau.capacite > 0:
                    taux_remplissage = (inscrits_creneau / creneau.capacite) * 100
                
                # On crée l'objet StatCreneauBus
                stat_creneau = StatCreneauBus(
                    creneau=creneau,
                    inscrits=inscrits_creneau,
                    restants=restants_creneau,
                    taux_remplissage=round(taux_remplissage, 2) # Arrondi à 2 décimales
                )
                stats_par_creneau_list.append(stat_creneau)

        # --- 3. Assemblage final ---
        
        # On crée l'objet StatistiquesEvenement final 
        stats_finales = StatistiquesEvenement(
            total_inscrits=total_inscrits,
            restants_evenement=restants_evenement,
            stats_par_creneau_bus=stats_par_creneau_list
        )
        
        return stats_finales
        