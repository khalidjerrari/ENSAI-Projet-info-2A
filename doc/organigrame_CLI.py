from graphviz import Digraph

# Création du diagramme
dot = Digraph("ReservationMenu", format="png")
dot.attr(rankdir="TB", size="8")

# Nœuds
dot.node("start", "DÉBUT", shape="oval")
dot.node("menu", "Afficher MENU\n1. Réserver\n2. Voir réservations\n3. Annuler\n0. Quitter", shape="rectangle")
dot.node("choix", "Lire choix utilisateur", shape="parallelogram")
dot.node("valid", "Choix valide ?", shape="diamond")
dot.node("erreur", "Message erreur\nRetour menu", shape="rectangle")

# Actions
dot.node("reserver", "Réserver :\nDemander nom + place\nAjouter réservation", shape="rectangle")
dot.node("voir", "Voir :\nAfficher réservations", shape="rectangle")
dot.node("annuler", "Annuler :\nDemander nom/ID\nSupprimer réservation", shape="rectangle")
dot.node("fin", "FIN", shape="oval")

# Liens
dot.edge("start", "menu")
dot.edge("menu", "choix")
dot.edge("choix", "valid")

# Choix valide ?
dot.edge("valid", "erreur", label="Non")
dot.edge("erreur", "menu")
dot.edge("valid", "reserver", label="Oui & Choix 1")
dot.edge("valid", "voir", label="Oui & Choix 2")
dot.edge("valid", "annuler", label="Oui & Choix 3")
dot.edge("valid", "fin", label="Oui & Choix 0")

# Boucles retour menu
dot.edge("reserver", "menu")
dot.edge("voir", "menu")
dot.edge("annuler", "menu")

# Sauvegarde sans extension (Graphviz ajoutera .png)
output_path = "organigramme_CLI"
dot.render(output_path, format="png", cleanup=True)
