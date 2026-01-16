# TP7 - Architecture Orientée Graphe (Neo4j)

## Architecture Globale

Ce projet met en œuvre une architecture NoSQL multi-technologies :

1.  **Source de données** : API Météo (Meteoblue).
2.  **Stockage Document (Data Lake)** : MongoDB Atlas. Stocke l'historique brut et nettoyé des relevés.
3.  **Stockage Graphe (Relations)** : Neo4j. Modélise les relations entre les lieux et les conditions météorologiques.
4.  **Traitement** : Scripts Python pour l'ingestion (ETL) et la synchronisation.

### Flux de données
`API` -> `Python (AlimenteBddAvecApi.py)` -> `MongoDB` -> `Python (SyncMongoToNeo4j.py)` -> `Neo4j`

## Modèle de Données (Graphe)

### Nœuds (Nodes)
*   **Location** : Représente un point géographique.
    *   `lat`: Latitude
    *   `lon`: Longitude
*   **Weather** : Représente un relevé à un instant T.
    *   `temperature`: Température en °C
    *   `windspeed`: Vitesse du vent
    *   `time`: Horodatage du modèle météo

### Relations (Relationships)
*   `(:Weather)-[:LOCATED_AT]->(:Location)` : Indique où le relevé a été pris.

## Installation et Démarrage

1.  **Prérequis** :
    *   Python 3.x
    *   Compte MongoDB Atlas
    *   Instance Neo4j (Desktop, Docker ou AuraDB)

2.  **Configuration** :
    Ajoutez les variables suivantes à votre fichier `.env` :
    ```env
    MONGO_URI=mongodb+srv://...
    API_KEY=votre_api_key_meteoblue
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=votre_mot_de_passe
    ```

3.  **Lancement** :
    *   Pour lancer l'alimentation continue et la synchro temps réel :
        ```bash
        python AlimenteBddAvecApi.py
        ```
    *   Pour synchroniser manuellement l'historique existant :
        ```bash
        python SyncMongoToNeo4j.py
        ```

## Requêtes de Démonstration (Cypher)

Une fois les données dans Neo4j, vous pouvez exécuter ces requêtes dans le navigateur Neo4j (http://localhost:7474).

**1. Voir tous les relevés pour une localisation donnée :**
```cypher
MATCH (w:Weather)-[:LOCATED_AT]->(l:Location)
WHERE l.lat = 48.8808643
RETURN w.time, w.temperature, w.windspeed
ORDER BY w.time DESC
LIMIT 10;
```

**2. Trouver la température maximale enregistrée par lieu :**
```cypher
MATCH (w:Weather)-[:LOCATED_AT]->(l:Location)
RETURN l.lat, l.lon, MAX(w.temperature) as MaxTemp;
```

**3. Analyser les corrélations (ex: Vent fort et Température) :**
```cypher
MATCH (w:Weather)
WHERE w.windspeed > 5 AND w.temperature < 10
RETURN w
```

**4. Supprimer tout le graphe (Reset) :**
```cypher
MATCH (n) DETACH DELETE n;
```