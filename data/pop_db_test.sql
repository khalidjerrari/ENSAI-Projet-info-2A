-- 1) UTILISATEUR
INSERT INTO utilisateur (nom, prenom, telephone, email, mot_de_passe, administrateur)
VALUES
('Dupont', 'Alice', '0601020304', 'alice.dupont@email.com', '$2b$12$kasVuw8LUvVK3anAskV40.ATzMUuUF5r9sRIuJc17BG4o2G/XKtyi', FALSE),
('Martin', 'Bob', '0605060708', 'bob.martin@email.com', '$2b$12$ZI9goAGUifVgF7dcZbNvgOjKED/Bfo193c5BDQW5RSaNxvkqu9QYa', TRUE),
('Durand', 'Caroline', '0608091011', 'caroline.durand@email.com', 'mdpCaroline123', FALSE),
('Petit', 'David', '0611121314', 'david.petit@email.com', 'mdpDavid123', FALSE);

-- 2) EVENEMENT (avant BUS, à cause de la FK dans BUS)
INSERT INTO evenement (fk_utilisateur, titre, adresse, ville, date_evenement, description, capacite, categorie, statut)
VALUES
(1, 'Conférence Tech', '10 Rue de Paris', 'Lyon', '2025-11-30', 'Événement sur les nouvelles technologies.', 30, 'Technologie', 'pas encore finalisé'),
(2, 'Salon de l’Art', '5 Avenue de Nice', 'Nice', '2025-12-01', 'Exposition d’art contemporain.', 50, 'Art', 'pas encore finalisé'),
(3, 'Match de Football', 'Stade National', 'Bruxelles', '2025-12-02', 'Rencontre sportive locale.', 40, 'Sport', 'pas encore finalisé'),
(4, 'Festival de Musique', 'Parc Central', 'Toulouse', '2025-12-03', 'Concert en plein air.', 60, 'Musique', 'pas encore finalisé');

-- 3) BUS (ajout de la colonne description requise)
INSERT INTO bus (fk_evenement, matricule, nombre_places, direction, description)
VALUES
(1, 'BUS-002', 50, 'aller',  'Bus 1 aller'),
(1, 'BUS-001', 50, 'retour', 'Bus 1 retour'),
(2, 'BUS-002', 50, 'aller',  'Bus 2 aller'),
(2, 'BUS-003', 50, 'retour', 'Bus 2 retour'),
(3, 'BUS-002', 50, 'aller',  'Bus 3 aller'),
(3, 'BUS-001', 50, 'retour', 'Bus 3 retour'),
(4, 'BUS-002', 50, 'aller',  'Bus 4 aller'),
(4, 'BUS-003', 50, 'retour', 'Bus 4 retour');

-- 4) RESERVATION (2e ligne complétée avec la 7e valeur manquante)
INSERT INTO reservation (fk_utilisateur, fk_evenement, bus_aller, bus_retour, adherent, sam, boisson)
VALUES
(1, 1, TRUE,  TRUE,  TRUE,  FALSE, TRUE),
(2, 2, FALSE, FALSE, TRUE,  FALSE, FALSE),
(3, 3, TRUE,  FALSE, TRUE,  TRUE,  TRUE),
(4, 4, FALSE, TRUE,  FALSE, FALSE, TRUE);

-- 5) COMMENTAIRE
INSERT INTO commentaire (fk_reservation, fk_utilisateur, note, avis)
VALUES
(1, 1, 5, 'Voyage très agréable et confortable. L’événement "Conférence Tech" était très enrichissant.'),
(2, 2, 4, 'Bon service, mais un peu de retard. Le "Salon de l’Art" était bien organisé et intéressant.'),
(3, 3, 3, 'Moyen, le bus était un peu vieux. Le match "Match de Football" était animé, mais la place était limitée.'),
(4, 4, 5, 'Excellent trajet et personnel sympathique. Le "Festival de Musique" a été un vrai succès !');
