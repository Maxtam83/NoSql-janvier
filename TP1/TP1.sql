CREATE TABLE utilisateurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE produits (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    prix DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    description TEXT
);

CREATE TABLE commandes (
    id SERIAL PRIMARY KEY,
    utilisateur_id INT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(50) DEFAULT 'en attente',
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
);

CREATE TABLE panier (
    id SERIAL PRIMARY KEY,
    commande_id INT NOT NULL,
    produit_id INT NOT NULL,
    quantite INT NOT NULL,
    prix_unitaire DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (commande_id) REFERENCES commandes(id),
    FOREIGN KEY (produit_id) REFERENCES produits(id)
);

CREATE TABLE avis (
    id SERIAL PRIMARY KEY,
    utilisateur_id INT NOT NULL,
    produit_id INT NOT NULL,
    note INT CHECK (note >= 1 AND note <= 5),
    commentaire TEXT,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id),
    FOREIGN KEY (produit_id) REFERENCES produits(id)
);

CREATE TABLE journaux_activite (
    id SERIAL PRIMARY KEY,
    utilisateur_id INT,
    action VARCHAR(255) NOT NULL,
    horodatage TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
);

-- REQUETE INSERT

INSERT INTO utilisateurs (nom, email, mot_de_passe) VALUES
('Alice Dupont', 'alice.dupont@example.com', 'motdepasse123'),
('Bob Martin', 'bob.martin@example.com', 'azerty456'),
('Claire Petit', 'claire.petit@example.com', 'password789'),
('David Leroy', 'david.leroy@example.com', 'monsecret!'),
('Émilie Moreau', 'emilie.moreau@example.com', 'soleil2023');

INSERT INTO produits (nom, prix, stock, description) VALUES
('Ordinateur Portable', 1200.00, 50, 'Un ordinateur portable puissant pour le travail et les loisirs.'),
('Smartphone Android', 750.00, 120, 'Le dernier smartphone avec un appareil photo incroyable.'),
('Casque Audio Bluetooth', 150.00, 200, 'Casque sans fil avec réduction de bruit active.'),
('Souris Ergonomique', 30.00, 300, 'Souris confortable pour une utilisation prolongée.'),
('Clavier Mécanique', 90.00, 100, 'Clavier robuste avec des touches réactives.'),
('Écran 27 pouces', 300.00, 75, 'Moniteur haute résolution pour une expérience visuelle immersive.');

INSERT INTO commandes (utilisateur_id, statut) VALUES
(1, 'livrée'),
(2, 'en attente'),
(1, 'expédiée'),
(3, 'annulée'),
(4, 'livrée');

INSERT INTO panier (commande_id, produit_id, quantite, prix_unitaire) VALUES
(1, 1, 1, 1200.00),
(1, 3, 1, 150.00),
(2, 2, 2, 750.00),
(3, 1, 1, 1200.00),
(3, 4, 1, 30.00),
(4, 5, 1, 90.00),
(5, 6, 1, 300.00);

INSERT INTO avis (utilisateur_id, produit_id, note, commentaire) VALUES
(1, 1, 5, 'Excellent ordinateur, très rapide et performant.'),
(2, 2, 4, 'Bon smartphone, mais la batterie pourrait être meilleure.'),
(1, 3, 5, 'Très bon casque, son impeccable et confortable.'),
(3, 5, 3, 'Clavier correct pour le prix, mais un peu bruyant.'),
(4, 6, 5, 'Superbe écran, les couleurs sont magnifiques.');

INSERT INTO journaux_activite (utilisateur_id, action) VALUES
(1, 'Connexion réussie'),
(2, 'Ajout produit au panier'),
(1, 'Commande passée'),
(3, 'Mise à jour profil'),
(4, 'Consultation produit'),
(NULL, 'Tentative de connexion échouée');

-- EXEMPLE DE JOINTURE

-- Sélectionne toutes les commandes avec les informations de l'utilisateur et les détails des produits commandés.
SELECT
    c.id AS commande_id,
    u.nom AS nom_utilisateur,
    u.email,
    c.date AS date_commande,
    c.statut,
    p.nom AS nom_produit,
    pa.quantite,
    pa.prix_unitaire
FROM
    commandes c
JOIN
    utilisateurs u ON c.utilisateur_id = u.id
JOIN
    panier pa ON c.id = pa.commande_id
JOIN
    produits p ON pa.produit_id = p.id
ORDER BY
    c.date DESC;

-- Affiche les avis des utilisateurs pour chaque produit, incluant le nom de l'utilisateur et le nom du produit.
SELECT
    a.id AS avis_id,
    u.nom AS nom_utilisateur,
    p.nom AS nom_produit,
    a.note,
    a.commentaire
FROM
    avis a
JOIN
    utilisateurs u ON a.utilisateur_id = u.id
JOIN
    produits p ON a.produit_id = p.id

-- Liste tous les produits et, s'ils ont été commandés, affiche la quantité totale commandée.
SELECT
    p.nom AS nom_produit,
    p.prix,
    p.stock,
    COALESCE(SUM(pa.quantite), 0) AS total_commandes
FROM
    produits p
LEFT JOIN
    panier pa ON p.id = pa.produit_id
GROUP BY
    p.id, p.nom, p.prix, p.stock
ORDER BY
    total_commandes DESC;

-- Récupère toutes les activités enregistrées, en associant l'utilisateur si l'action a été effectuée par un utilisateur enregistré.
SELECT
    ja.id AS journal_id,
    COALESCE(u.nom, 'Utilisateur inconnu') AS nom_utilisateur,
    ja.action,
    ja.horodatage
FROM
    journaux_activite ja
LEFT JOIN
    utilisateurs u ON ja.utilisateur_id = u.id