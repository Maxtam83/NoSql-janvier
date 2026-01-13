import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from testConnexionAtlas import connect_to_mongodb_atlas


load_dotenv()

def fetch_weather_data(api_key):
    """
    Récupère les données météorologiques de l'API meteoblue.
    """
    if not api_key:
        print("API_KEY introuvable. Veuillez le définir.")
        return None
    
    api = f"https://my.meteoblue.com/packages/current?lat=48.901020&lon=2.19&apikey={api_key}"
    
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

def insert_weather_data(db, data):
    """
    Insère les données météorologiques dans la collection 'current_weather' de la base de données MongoDB.
    """
    if db is None:
        print("La connexion à la base de données n'est pas établie.")
        return
    
    try:
        collection = db.current_weather
        collection.insert_one(data)
        print("Données météorologiques insérées avec succès dans MongoDB.")
    except Exception as e:
        print(f"Erreur lors de l'insertion des données dans MongoDB : {e}")

if __name__ == "__main__":
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        print("API_KEY introuvable dans le fichier .env. Veuillez le définir.")
        exit()

    # Connexion à MongoDB Atlas
    db_atlas = connect_to_mongodb_atlas()

    if db_atlas is not None:
        # Récupération des données météorologiques
        weather_data = fetch_weather_data(API_KEY)

        if weather_data is not None:
            # Insertion des données dans la base de données
            insert_weather_data(db_atlas, weather_data)
        else:
            print("Aucune donnée météorologique à insérer.")
    else:
        print("Impossible de se connecter à la base de données MongoDB Atlas.")