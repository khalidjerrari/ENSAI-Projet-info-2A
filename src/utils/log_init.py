import os
import logging
import logging.config
import yaml


def initialiser_logs(nom_application: str = "Application") -> None:
    """
    Initialise la configuration des logs à partir du fichier YAML.
    Si le fichier n'existe pas, un fallback par défaut est utilisé.
    """

    # Chemin absolu du répertoire courant (celui du script principal)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    projet_root = os.path.abspath(os.path.join(base_dir, os.pardir))
    config_path = os.path.join(projet_root, "logging_config.yml")

    # Création du dossier logs à la racine s’il n’existe pas
    logs_dir = os.path.join(projet_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    try:
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    except FileNotFoundError:
        print(f"Fichier de configuration des logs introuvable : {config_path}")
        print("Utilisation d’une configuration de logs par défaut.")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(os.path.join(logs_dir, "application.log"), encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
    except Exception as e:
        print(f"Erreur lors du chargement du fichier logging_config.yml : {e}")
        logging.basicConfig(level=logging.INFO)

    # Message d’en-tête dans les logs
    logging.info("-" * 60)
    logging.info(f"Lancement de l’application : {nom_application}")
    logging.info("-" * 60)
