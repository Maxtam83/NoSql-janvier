import os
import requests
import time
import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from SyncMongoToNeo4j import WeatherGraphSync

load_dotenv()

def connect_to_mongodb_atlas():
    """
    Initialise une connexion à la base de données MongoDB Atlas et renvoie l'objet de la BDD si réussie.
    Sinon, affiche l'erreur.
    """
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        print("MONGO_URI not found in .env file. Please set it.")
        return None
    
    try:
        client = MongoClient(MONGO_URI)
        client.admin.command('ping')
        print("Connexion à MongoDB Atlas réussie.")
        return client.sample_mflix
    except ConnectionFailure as e:
        print(f"Erreur de connexion à MongoDB Atlas: {e}")
        return None

def fetch_weather_data(api_key):
    """
    Récupère les données météorologiques de l'API meteoblue.
    """
    if not api_key:
        print("API_KEY introuvable. Veuillez le définir.")
        return None
    
    api = f"https://my.meteoblue.com/packages/current?lat=48.8808643&lon=2.3489429&apikey={api_key}"
    
    try:
        response = requests.get(api)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as erreur:
        print(f"Erreur lors de la récupération des données de l'API : {erreur}")
        return None
    except ValueError as erreur:
        print(f"Erreur lors du décodage JSON de l'API : {erreur}")
        return None

def insert_weather_data(db, data, collection_name='current_weather'):
    """
    Insère les données météorologiques dans la collection 'current_weather' de la base de données MongoDB.
    """
    if db is None:
        print("La connexion à la base de données n'est pas établie.")
        return
    
    try:
        collection = db[collection_name]
        collection.insert_one(data)
        print("Données météorologiques insérées avec succès dans MongoDB :",  datetime.datetime.now().strftime("%H:%M:%S") )
    except Exception as e:
        print(f"Erreur lors de l'insertion des données dans MongoDB : {e}")

def clean_weather_data(data):
    if not data or 'data_current' not in data or 'metadata' not in data:
        return None

    cleaned_data = {
        'time': data['metadata'].get('modelrun_updatetime_utc'),
        'last_update': data['data_current'].get('time'),
        'lat': data['metadata'].get('latitude'),
        'lon': data['metadata'].get('longitude'),
        'temperature': data['data_current'].get('temperature'),
        'windspeed': data['data_current'].get('windspeed'),
        'zenithangle': data['data_current'].get('zenithangle')
    }
    return cleaned_data

def get_weather_data_and_instert_clean_data_to_mongodb():
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        print("API_KEY introuvable dans le fichier .env. Veuillez le définir.")
        exit()

    # Connexion à MongoDB Atlas
    db_atlas = connect_to_mongodb_atlas()

    if db_atlas is not None:
        # Récupération des données météorologiques et clean
        weather_data = fetch_weather_data(API_KEY)
        weather_data = clean_weather_data(weather_data)

        if weather_data is not None:
            # Insertion des données dans la base de données
            insert_weather_data(db_atlas, weather_data,"current_weather_clean")
            
            # Synchronisation vers Neo4j
            try:
                syncer = WeatherGraphSync()
                syncer.sync_data(weather_data)
                syncer.close()
            except Exception as e:
                print(f"Erreur lors de la synchro Neo4j : {e}")
        else:
            print("Aucune donnée météorologique à insérer.")
    else:
        print("Impossible de se connecter à la base de données MongoDB Atlas.")

if __name__ == "__main__":
    # get_weather_data_and_insert_to_mongodb()
    while(True):
        get_weather_data_and_instert_clean_data_to_mongodb()
        time.sleep(600)