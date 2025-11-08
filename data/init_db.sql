-----------------------------------------------------
-- TABLE : Utilisateur
-----------------------------------------------------

DROP TABLE IF EXISTS utilisateur CASCADE;
CREATE TABLE utilisateur (
    id_utilisateur SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    telephone VARCHAR(20),
    email VARCHAR(100) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(256) NOT NULL,
    administrateur BOOLEAN DEFAULT FALSE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-----------------------------------------------------
-- TABLE : Événement
-----------------------------------------------------

DROP TABLE IF EXISTS evenement CASCADE;
CREATE TABLE evenement (
    id_evenement SERIAL PRIMARY KEY,
    fk_utilisateur INT REFERENCES utilisateur(id_utilisateur) ON DELETE SET NULL,
    titre VARCHAR(150) NOT NULL,
    adresse VARCHAR(100),
    ville VARCHAR(100),
    date_evenement DATE NOT NULL,
    description TEXT,
    capacite INT NOT NULL,
    date_creation TIMESTAMP DEFAULT NOW(),
    categorie VARCHAR(50),
    statut VARCHAR(50) DEFAULT 'pas encore finalisé'
        CHECK (statut IN ('disponible en ligne', 'déjà réalisé', 'annulé', 'pas encore finalisé'))
);

-----------------------------------------------------
-- TABLE : Bus
-----------------------------------------------------

DROP TABLE IF EXISTS bus CASCADE;
CREATE TABLE bus (
    id_bus SERIAL PRIMARY KEY,
    fk_evenement INT REFERENCES evenement(id_evenement) ON DELETE SET NULL,
    matricule VARCHAR(20),
    nombre_places INT NOT NULL CHECK (nombre_places > 0),
    direction VARCHAR(10) DEFAULT 'aller' CHECK(direction IN ('aller', 'retour')),
    description VARCHAR(100) UNIQUE NOT NULL
);

-----------------------------------------------------
-- TABLE : Réservation
-----------------------------------------------------

DROP TABLE IF EXISTS reservation CASCADE;
CREATE TABLE reservation (
    id_reservation SERIAL PRIMARY KEY,
    fk_utilisateur INT NOT NULL REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    fk_evenement INT NOT NULL REFERENCES evenement(id_evenement) ON DELETE CASCADE,
    bus_aller BOOLEAN DEFAULT FALSE,
    bus_retour BOOLEAN DEFAULT FALSE,
    date_reservation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    adherent BOOLEAN DEFAULT FALSE,
    sam BOOLEAN DEFAULT FALSE,
    boisson BOOLEAN DEFAULT FALSE,

    -- ✅ Correction ici :
    -- Un utilisateur ne peut réserver qu'une seule fois le même événement
    CONSTRAINT reservation_unique_user_event UNIQUE (fk_utilisateur, fk_evenement)
);

-----------------------------------------------------
-- TABLE : Commentaire
-----------------------------------------------------

DROP TABLE IF EXISTS commentaire CASCADE;
CREATE TABLE commentaire (
    id_commentaire SERIAL PRIMARY KEY,                  
    fk_reservation INT NOT NULL REFERENCES reservation(id_reservation) ON DELETE CASCADE,
    fk_utilisateur INT NOT NULL REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    note INT CHECK (note BETWEEN 1 AND 5),             
    avis TEXT,                                        
    date_commentaire TIMESTAMP DEFAULT NOW()          
);
