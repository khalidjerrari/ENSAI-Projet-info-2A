
---

#  Shotgun ENSAI – 2nd Year Project

> Event and reservation management application for the ENSAI Student Union (BDE)

---

##  Table of Contents

* [About](#-about)
* [Main Features](#-main-features)
* [Prerequisites](#-prerequisites)
* [Installation](#-installation)
* [Configuration](#-configuration)
* [Usage](#-usage)
* [Tests](#-tests)
* [Logs](#-logs)
* [Continuous Integration](#-continuous-integration)
* [Project Structure](#-project-structure)

---

##  About

This application serves as a foundation for the 2nd-year IT project at ENSAI. It demonstrates software development best practices through a complete event management application.

##  Main Features

###  Layered Architecture

The application follows a modular and maintainable architecture:

* **DAO (Data Access Object)**: Manages database access
* **Service**: Business logic and application processes
* **View**: Command-line user interface
* **Business Object**: Data structures representing domain entities

This separation improves code readability, maintainability, and extensibility.

###  PostgreSQL Database

* Centralized data storage
* Optimized SQL queries
* Management of relationships between entities

###  Command-Line Interface

Interactive interface built with **InquirerPy** providing:

* Intuitive interactive menus
* Guided navigation
* Secure user input

###  Email Sending via Brevo API

Integration of the Brevo API for:

* Automated notifications
* User action confirmations
* Communication workflows

---

##  Prerequisites

Before starting, ensure the following are installed:

* [Visual Studio Code](https://code.visualstudio.com/)
* [Python 3.13](https://www.python.org/)
* [Git](https://git-scm.com/)
* A [PostgreSQL](https://www.postgresql.org/) database
* Access to [Onyxia-SSPCloud](https://datalab.sspcloud.fr/my-services)

---

##  Installation

### 1. Clone the Repository

Open **Git Bash** and run:

```bash
git clone https://github.com/khalidjerrari/ENSAI-Projet-info-2A.git
```

### 2. Open the Project in VSCode

1. Launch **Visual Studio Code** on Onyxia
2. Go to **File > Open Folder**
3. Select the folder `ENSAI-projet-info-2A`

⚠️ **Important**: `ENSAI-projet-info-2A` must be the root in your Explorer. Otherwise, the application will not launch correctly.

### 3. Install Python Dependencies

In the terminal (Git Bash), run:

```bash
pip install -r requirements.txt
pip list  # Verify installation
```

---

##  Configuration

### 1. Start PostgreSQL

Start the **PostgreSQL** service on Onyxia.

### 2. Create the `.env` File

At the root of the project, create a `.env` file with the following content:

```env
PYTHONPATH=src

# PostgreSQL Configuration
POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_DATABASE=
POSTGRES_USER=
POSTGRES_PASSWORD=

# Test Schema
POSTGRES_SCHEMA=projet_test_dao

# Brevo Configuration
TOKEN_BREVO=
EMAIL_BREVO=
```

Fill in the values with your connection information.

### 3. Verify the Connection

Ensure that:

* The database is accessible using the `.env` settings
* The schema `projet_test_dao` exists for unit testing

---

##  Usage

### Launch the Application

```bash
python src/main.py
```

On the first launch, choose **Reset database** to:

* Run the program `src/utils/reset_database.py`
* Initialize the database using the SQL scripts in the `data` folder

---

##  Tests

### Run All Tests

```bash
pytest -v
# or if pytest is not in PATH
python -m pytest -v
```

### DAO Tests

DAO unit tests use:

* A dedicated schema (`projet_test_dao`) to avoid polluting real data
* Test data from `data/pop_db_test.sql`

### Test Coverage

Generate a coverage report using [Coverage](https://coverage.readthedocs.io/):

```bash
coverage run -m pytest          # Run tests with coverage
coverage report -m              # Display report in console
coverage html                   # Generate HTML report
```

Open `coverage_report/index.html` in your browser.

> 💡 The `.coveragerc` file allows you to customize Coverage settings

---

##  Logs

### Configuration

Logs are initialized in `src/utils/log_init.py` and configured via `logging_config.yml`.

**To change the log level**: edit the `level` tag in `logging_config.yml`.

### Log Decorator

A decorator in `src/utils/log_decorator.py` automatically logs:

* Input parameters
* Output value


---

## 🔄 Continuous Integration

### GitHub Actions Pipeline

The file `.github/workflows/ci.yml` automatically triggers a pipeline on each *push*, which:

1. ✅ Creates an Ubuntu container
2. ✅ Installs Python
3. ✅ Installs dependencies
4. ✅ Runs tests (services only)
5. ✅ Analyses code with **pylint** (minimum score: 7.5/10)

### Viewing Results

Check the **Actions** tab on your GitHub repository to monitor the pipeline.

---

## 📁 Project Structure

### Root Files

| File               | Description                       |
| ------------------ | --------------------------------- |
| `README.md`        | Main project documentation        |
| `LICENSE`          | License and usage conditions      |
| `requirements.txt` | Python dependencies               |
| `.env`             | Environment variables (to create) |

### Configuration Files

| File                       | Description                      |
| -------------------------- | -------------------------------- |
| `.github/workflows/ci.yml` | CI/CD pipeline configuration     |
| `.vscode/settings.json`    | VSCode project-specific settings |
| `.coveragerc`              | Test coverage configuration      |
| `.gitignore`               | Git ignore files/folders         |
| `logging_config.yml`       | Logging configuration            |

### Folders

| Folder  | Description                                     |
| ------- | ----------------------------------------------- |
| `data/` | SQL scripts and datasets                        |
| `doc/`  | UML diagrams and documentation                  |
| `src/`  | Source code organized in a layered architecture |

### Source Code Organization (`src/`)

```
src/
├── business_object/    # Domain entities
├── dao/               # Data access
├── service/           # Business logic
├── view/              # User interface
│   ├── accueil/
│   ├── auth/
│   ├── client/
│   ├── administrateur/
│   ├── consulter/
│   ├── evenement/
│   └── reservations/
├── utils/             # Utilities (logs, security, etc.)
├── tests/             # Unit tests
└── main.py           # Application entry point
```

---

##  Contributors

Project developed as part of the ENSAI 2nd-year curriculum.

---

##  License

See the [LICENSE](LICENSE) file for details.

---
