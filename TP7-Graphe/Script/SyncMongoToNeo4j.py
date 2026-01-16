import os
from dotenv import load_dotenv
from pymongo import MongoClient
from neo4j import GraphDatabase

load_dotenv()

class WeatherGraphSync:
    def __init__(self):
        # Configuration Neo4j
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def sync_data(self, mongo_data):
        """
        Synchronise un document météo (ou une liste) vers Neo4j.
        """
        if not mongo_data:
            return

        if not isinstance(mongo_data, list):
            mongo_data = [mongo_data]

        with self.driver.session() as session:
            for record in mongo_data:
                session.execute_write(self._create_weather_nodes, record)
                print(f"Donnée synchronisée dans Neo4j : {record.get('last_update')}")

    @staticmethod
    def _create_weather_nodes(tx, data):
        # Requête Cypher pour créer les noeuds et la relation
        # On utilise MERGE pour éviter les doublons (idempotence)
        query = """
        MERGE (l:Location {lat: $lat, lon: $lon})
        
        MERGE (w:Weather {time: $time})
        SET w.temperature = $temperature,
            w.windspeed = $windspeed,
            w.zenithangle = $zenithangle,
            w.last_update = $last_update

        MERGE (w)-[:LOCATED_AT]->(l)
        """
        
        tx.run(query, 
               lat=data.get('lat'), 
               lon=data.get('lon'),
               time=data.get('time'), # modelrun_updatetime_utc
               temperature=data.get('temperature'),
               windspeed=data.get('windspeed'),
               zenithangle=data.get('zenithangle'),
               last_update=data.get('last_update'))

def run_full_sync():
    """
    Fonction utilitaire pour synchroniser toute la collection existante.
    """
    # Connexion Mongo (Reprise de la logique existante ou nouvelle connexion)
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        print("MONGO_URI manquant.")
        return

    client = MongoClient(MONGO_URI)
    db = client.sample_mflix # Ou le nom de votre DB défini dans le projet
    collection = db["current_weather_clean"]
    
    syncer = WeatherGraphSync()
    
    try:
        cursor = collection.find({})
        print("Début de la synchronisation complète...")
        for doc in cursor:
            syncer.sync_data(doc)
        print("Synchronisation terminée.")
    finally:
        syncer.close()
        client.close()

if __name__ == "__main__":
    run_full_sync()