from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

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

if __name__ == "__main__":
   
    # Test de connexion à la base de données Atlas
    print("\n--- Test de connexion à MongoDB Atlas ---")
    db_atlas = connect_to_mongodb_atlas()
    if db_atlas is not None:
        print(f"Collections dans la base de données '{db_atlas.name}': {db_atlas.list_collection_names()}")