import logging
import dotenv


from utils.log_init import initialiser_logs
from view.accueil.accueil_vue import AccueilVue


if __name__ == "__main__":
    dotenv.load_dotenv(override=True)
    initialiser_logs("Application")

    vue_courante = AccueilVue("Bienvenue")
    nb_erreurs = 0

    while vue_courante:
        if nb_erreurs > 100:
            print("Le programme recense trop d'erreurs et va s'arrêter")
            break
        try:
            vue_courante.afficher()
            vue_courante = vue_courante.choisir_menu()
        except Exception as e:
            logging.exception(e)
            nb_erreurs += 1
            vue_courante = AccueilVue("Une erreur est survenue, retour au menu principal")

    print("----------------------------------")
    print("Au revoir")
    logging.info("Fin de l'application")
