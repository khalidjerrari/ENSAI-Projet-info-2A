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
-- TABLE : Bus
-----------------------------------------------------

DROP TABLE IF EXISTS bus CASCADE;
CREATE TABLE bus (
    id_bus SERIAL PRIMARY KEY,
    matricule VARCHAR(50) UNIQUE NOT NULL,
    nombre_places INT NOT NULL CHECK (nombre_places > 0)
);

-----------------------------------------------------
-- TABLE : Transport
-----------------------------------------------------

DROP TABLE IF EXISTS transport CASCADE;
CREATE TABLE transport (
    id_transport SERIAL PRIMARY KEY,
    fk_bus INT NOT NULL REFERENCES bus(id_bus) ON DELETE CASCADE,
    ville_depart VARCHAR(100) NOT NULL,
    ville_arrivee VARCHAR(100) NOT NULL,
    date_transport DATE NOT NULL,
    CONSTRAINT transport_unique UNIQUE (fk_bus, date_transport, ville_depart, ville_arrivee)
);

-----------------------------------------------------
-- TABLE : Événement
-----------------------------------------------------

DROP TABLE IF EXISTS evenement CASCADE;
CREATE TABLE evenement (
    id_evenement SERIAL PRIMARY KEY,
    fk_transport INT NOT NULL REFERENCES transport(id_transport) ON DELETE CASCADE,
    fk_utilisateur INT REFERENCES utilisateur(id_utilisateur) ON DELETE SET NULL,
    titre VARCHAR(150) NOT NULL,
    adresse VARCHAR(255),
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
-- TABLE : Réservation
-----------------------------------------------------

DROP TABLE IF EXISTS reservation CASCADE;
CREATE TABLE reservation (
    id_reservation SERIAL PRIMARY KEY,
    fk_utilisateur INT NOT NULL REFERENCES utilisateur(id_utilisateur) ON DELETE CASCADE,
    fk_transport INT NOT NULL REFERENCES transport(id_transport) ON DELETE CASCADE,
    date_reservation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    adherent BOOLEAN DEFAULT FALSE,
    sam BOOLEAN DEFAULT FALSE,
    boisson BOOLEAN DEFAULT FALSE,
    -- Un utilisateur ne peut réserver qu'une seule fois un même trajet 
    CONSTRAINT reservation_unique UNIQUE (fk_utilisateur, fk_transport)
);

-----------------------------------------------------
-- TABLE : Commentaire
-----------------------------------------------------

DROP TABLE IF EXISTS commentaire CASCADE;
CREATE TABLE commentaire (
    id_commentaire SERIAL PRIMARY KEY,                  
    fk_reservation INT NOT NULL                         
        REFERENCES reservation(id_reservation) 
        ON DELETE CASCADE,
    fk_utilisateur INT NOT NULL                         
        REFERENCES utilisateur(id_utilisateur) 
        ON DELETE CASCADE,
    note INT CHECK (note BETWEEN 1 AND 5),             
    avis TEXT,                                        
    date_commentaire TIMESTAMP DEFAULT NOW()          
);
