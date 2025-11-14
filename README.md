# Shotgun info Project-Documentatoion

This project a simple application that serves as a foundation for the 2nd year IT project at ENSAI.

It includes several technical components designed to illustrate and support good software-development practices:

--Main Features--

--Layered  Architecture 
The application follows a modular, layered architecture composed of:

-DAO (Data Acces Object): Manages data access and interactions with the database

-Service: Contains business logic and core application process

-View: Terminal based user interface

-Business Object: Data structures representing domain entities
This separation improves readability, maintainability, and future extensibility

--Database Connection
A database connection is integrated into the project to:

-store query data
-centralize information
-demonstrate SQL queries

--Command line interface
The application includes a terminal user interface built with InquirerPy, allowing for:

-interactive menus
-intuitive navigation
-guided user input

--Email sending with the Brevo API
The project integrates the Brevo API to handle email sending. This allows the application to:

-send automated notifications
-confirm user actions
-support communication workflows within the system


## :arrow_forward: Software and tools

- [Visual Studio Code](https://code.visualstudio.com/)
- [Python 3.13](https://www.python.org/)
- [Git](https://git-scm.com/)
- A [PostgreSQL](https://www.postgresql.org/) database
-[Onyxia-SSPCloud](https://datalab.sspcloud.fr/my-services)


## :arrow_forward: Clone the repository

- [ ] Open VSCode
- [ ] Open **Git Bash**
- [ ] Clone the repo
  - `git clone https://github.com/khalidjerrari/ENSAI-Projet-info-2A.git`


### Open Folder

- [ ] Open **Visual Studio Code** service on Onyxia
- [ ] File > Open Folder
- [ ] Select folder *ENSAI-projet-info-2A*
  - *ENSAI-projet-info-2A* should be the root of your Explorer
  - :warning: if not the application will not launch. Retry open folder
-[] Start the **PostgreSQL** service on Onyxia 
-[] Verify that database is accessible using the information in your .env file:

```POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DATABASE=
POSTGRES_USER=
POSTGRES_PASSWORD=
```
-[] Ensure that the schema projet_test_dao exists for units testing

## Repository Files Overview


| Item                       | Description                                                              |
| -------------------------- | ------------------------------------------------------------------------ |
| `README.md`                | Provides useful information to present, install, and use the application |
| `LICENSE`                  | Specifies the usage rights and licensing terms for the repository        |

### Configuration files

This repository contains a large number of configuration files for setting the parameters of the various tools used.

Normally, for the purposes of your project, you won't need to modify these files, except for `.env` and `requirements.txt`.


| Item                       | Description                                                              |
| -------------------------- | ------------------------------------------------------------------------ |
| `.github/workflows/ci.yml` | Automated workflow that runs predefined tasks (like testing, linting, or deploying) |
| `.vscode/settings.json`    | Contains VS Code settings specific to this project                       |
| `.coveragerc`              | Setup for test coverage                                                  |
| `.gitignore`               | Lists the files and folders that should not be tracked by Git            |
| `logging_config.yml`       | Setup for logging                                                        |
| `requirements.txt`         | Lists the required Python packages for the project                       |

You will also need a `.env` file. See below.


### Folders

| Item                       | Description                                                              |
| -------------------------- | ------------------------------------------------------------------------ |
| `data`                     | SQL script containing data sets                                          |
| `doc`                      | UML diagrams, project status...                                          |
| `src`                      | Folder containing Python files organized using a layered architecture    |



### Settings files

This repository contains a large number of configuration files for setting the parameters of the various tools used.

Normally, for the purposes of your project, you won't need to modify these files, except for `.env` and `requirements.txt`.


## :arrow_forward: Install required packages

- [ ] In Git Bash, run the following commands to:
  - install all packages from file `requirements.txt`
  - list all packages

```bash
pip install -r requirements.txt
pip list
```


## :arrow_forward: Environment variables

You are now going to define environment variables to declare the database and webservice to which you are going to connect your python application.

At the root of the project :

- [ ] Create a file called `.env`
- [ ] Paste in and complete the elements below

```default
PYTHONPATH=src

POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DATABASE=
POSTGRES_USER=
POSTGRES_PASSWORD=

POSTGRES_SCHEMA=projet_test_dao

TOKEN_BREVO=
EMAIL_BREVO=
```
Launch the application with the commande `python src/main.py`


## :arrow_forward: Unit tests

- [ ] In Git Bash: `pytest -v` 
  - or `python -m pytest -v` if *pytest* has not been added to *PATH*


### TU DAO

To ensure tests are repeatable, safe, and **do not interfere with the real database**, we use a dedicated schema for unit testing.

The DAO unit tests use data from the `data/pop_db_test.sql` file.

This data is loaded into a separate schema (projet_test_dao) so as not to pollute the other data.


### Test coverage

It is also possible to generate test coverage using [Coverage](https://coverage.readthedocs.io/en/7.4.0/index.html)

:bulb: The `.coveragerc` file can be used to modify the settings

- [ ] `coverage run -m pytest`
- [ ] `coverage report -m`
- [ ] `coverage html`
  - Download and open coverage_report/index.html



## :arrow_forward: Launch the CLI application

This application provides a very basic graphical interface for navigating between different menus.

- [ ] In Git Bash: `python src/main.py`
- [ ] On first launch, choose **Reset database**
  - this calls the `src/utils/reset_database.py` program
  - which will itself execute the SQL scripts in the `data` folder


## :arrow_forward: Logs

It is initialised in the `src/utils/log_init.py` module:

- This is called when the application or webservice is started.
- It uses the `logging_config.yml` file for configuration.
  - to change the log level :arrow_right: *level* tag

A decorator has been created in `src/utils/log_decorator.py`.

When applied to a method, it will display in the logs :

- input parameters
- the output

The logs can be viewed in the `logs` folder.

Example of logs :

```
07/08/2024 09:07:07 - INFO     - ConnexionVue
07/08/2024 09:07:08 - INFO     -     JoueurService.se_connecter('a', '*****') - DEBUT
07/08/2024 09:07:08 - INFO     -         JoueurDao.se_connecter('a', '*****') - DEBUT
07/08/2024 09:07:08 - INFO     -         JoueurDao.se_connecter('a', '*****') - FIN
07/08/2024 09:07:08 - INFO     -            └─> Sortie : Joueur(a, 20 ans)
07/08/2024 09:07:08 - INFO     -     JoueurService.se_connecter('a', '*****') - FIN
07/08/2024 09:07:08 - INFO     -        └─> Sortie : Joueur(a, 20 ans)
07/08/2024 09:07:08 - INFO     - MenuJoueurVue
```



## :arrow_forward: Continuous integration (CI)

The repository contains a `.github/workflow/main.yml' file.

When you *push* on GitHub, it triggers a pipeline that will perform the following steps:

- Creating a container from an Ubuntu (Linux) image
  - In other words, it creates a virtual machine with just a Linux kernel.
- Install Python
- Install the required packages
- Run the unit tests (only the service tests, as it's more complicated to run the dao tests)
- Analyse the code with *pylint*
  - If the score is less than 7.5, the step will fail

You can check how this pipeline is progressing on your repository's GitHub page, *Actions* tab.