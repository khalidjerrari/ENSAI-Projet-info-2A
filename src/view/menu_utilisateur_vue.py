from InquirerPy import inquirer

from view.vue_abstraite import VueAbstraite
from view.session import Session

# Va falloir importer une certaine classe de service


class MenuJoueurVue(VueAbstraite):
    """Vue du menu du joueur

    Attributes
    ----------
    message=''
        str

    Returns
    ------
    view
        retourne la prochaine vue, celle qui est choisie par l'utilisateur
    """

    def choisir_menu(self):
        """Choix du menu suivant de l'utilisateur

        Return
        ------
        vue
            Retourne la vue choisie par l'utilisateur dans le terminal
        """

        print("\n" + "-" * 50 + "\nMenu Joueur\n" + "-" * 50 + "\n")

        choix = inquirer.select(
            message="Faites votre choix : ",
            choices=[
                "Afficher les joueurs de la base de données",
                "Afficher des pokemons (par appel à un Webservice)",
                "Infos de session",
                "Se déconnecter",
            ],
        ).execute()

        match choix:
            case "Se déconnecter":
                Session().deconnexion()
                from view.accueil.accueil_vue import AccueilVue

                return AccueilVue()

            case "Infos de session":
                return MenuJoueurVue(Session().afficher())

            case "Afficher les joueurs de la base de données":
                joueurs_str = JoueurService().afficher_tous() 
                return MenuJoueurVue(joueurs_str)

            case "Afficher des pokemons (par appel à un Webservice)":
                from view.pokemon_vue import PokemonVue

                return PokemonVue()  # à remplacer avec EvenementVue ou un truc comme ça
