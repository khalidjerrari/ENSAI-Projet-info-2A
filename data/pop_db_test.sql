INSERT INTO utilisateur (nom, prenom, telephone, email, mot_de_passe, administrateur)
VALUES
('Dupont', 'Alice', '0601020304', '','$2b$12$kasVuw8LUvVK3anAskV40.ATzMUuUF5r9sRIuJc17BG4o2G/XKtyi', FALSE),
('Martin', 'Bob', '0605060708', 'bob.martin@email.com','$2b$12$ZI9goAGUifVgF7dcZbNvgOjKED/Bfo193c5BDQW5RSaNxvkqu9QYa', TRUE),
('Durand', 'Caroline', '0608091011', 'caroline.durand@email.com', 'mdpCaroline123', FALSE),
('Petit', 'David', '0611121314', 'david.petit@email.com', 'mdpDavid123', FALSE);


INSERT INTO bus (matricule, nombre_places)
VALUES
('BUS-001', 50),
('BUS-002', 40),
('BUS-003', 60),
('BUS-004', 55);


INSERT INTO transport (fk_bus, ville_depart, ville_arrivee, date_transport)
VALUES
(1, 'Paris', 'Lyon', '2025-11-30'),
(2, 'Marseille', 'Nice', '2025-12-01'),
(3, 'Lille', 'Bruxelles', '2025-12-02'),
(4, 'Bordeaux', 'Toulouse', '2025-12-03');


INSERT INTO evenement (fk_transport, fk_utilisateur, titre, adresse, ville, date_evenement, description, capacite, categorie, statut)
VALUES
(1, 1, 'Conférence Tech', '10 Rue de Paris', 'Lyon', '2025-11-30', 'Événement sur les nouvelles technologies.', 30, 'Technologie', 'pas encore finalisé'),
(2, 2, 'Salon de l’Art', '5 Avenue de Nice', 'Nice', '2025-12-01', 'Exposition d’art contemporain.', 50, 'Art', 'pas encore finalisé'),
(3, 3, 'Match de Football', 'Stade National', 'Bruxelles', '2025-12-02', 'Rencontre sportive locale.', 40, 'Sport', 'pas encore finalisé'),
(4, 4, 'Festival de Musique', 'Parc Central', 'Toulouse', '2025-12-03', 'Concert en plein air.', 60, 'Musique', 'pas encore finalisé');


INSERT INTO reservation (fk_utilisateur, fk_transport, adherent, sam, boisson)
VALUES
(1, 1, TRUE, FALSE, TRUE),
(2, 2, FALSE, TRUE, FALSE),
(3, 3, TRUE, TRUE, TRUE),
(4, 4, FALSE, FALSE, TRUE);


INSERT INTO commentaire (fk_reservation, fk_utilisateur, note, avis)
VALUES
(1, 1, 5, 'Voyage très agréable et confortable. L’événement "Conférence Tech" était très enrichissant.'),
(2, 2, 4, 'Bon service, mais un peu de retard. Le "Salon de l’Art" était bien organisé et intéressant.'),
(3, 3, 3, 'Moyen, le bus était un peu vieux. Le match "Match de Football" était animé, mais la place était limitée.'),
(4, 4, 5, 'Excellent trajet et personnel sympathique. Le "Festival de Musique" a été un vrai succès !');
