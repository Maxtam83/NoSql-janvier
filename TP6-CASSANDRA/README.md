1) Créé un keyspace nommé mobility contenant une table 
destinée à stocker l’historique de disponibilité des stations Vélib

```bash
CREATE KEYSPACE mobility 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
```

```bash
USE mobility;
```

2) création table velib_status

```shell
CREATE TABLE velib_status (
    station_id int,
    name text,
    capacity int,
    bikes_available int,
    status_date timestamp,
    PRIMARY KEY (station_id, status_date)
) WITH CLUSTERING ORDER BY (status_date DESC);
```

3) requetes d'insertion de data
```shell
    INSERT INTO velib_status (station_id, name, capacity, bikes_available, status_date) 
    VALUES (16107, 'Benjamin Franklin', 35, 12, '2026-01-16 08:00:00');

    INSERT INTO velib_status (station_id, name, capacity, bikes_available, status_date) 
    VALUES (16107, 'Benjamin Franklin', 35, 8, '2026-01-16 09:00:00');

    INSERT INTO velib_status (station_id, name, capacity, bikes_available, status_date) 
    VALUES (12005, 'Gare Saint-Lazare', 50, 5, '2026-01-16 09:00:00');

```

4) exemple de requete

a) requete valide

```
SELECT * FROM velib_status WHERE station_id = 16107;
```

b) requete invalide (Cassandra refusera cette requête car elle n'inclut pas la clé de partition et nécessiterait de scanner tous les noeuds du cluster.)

```
SELECT * FROM velib_status WHERE bikes_available > 10;
```

4) rôle de la clé de partition

*Elle hache la valeur (ex: station_id) pour décider quel serveur stocke la donnée. C'est le secret de la scalabilité de Cassandra.*

5) différences de fonctionnement entre Cassandra et une base relationnelle.

*1. Pas de JOIN : On dénormalise les données.
 
2. Schéma rigide : On ne peut requêter que sur les colonnes indexées ou les clés de partition (sauf utilisation de ALLOW FILTERING, mais c'est une mauvaise pratique).*