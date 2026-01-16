from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from SyncMongoToNeo4j import WeatherGraphSync
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines (pratique pour le dev)
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes (GET, POST, PUT, DELETE...)
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not found in .env file. Please set it.")

client = None
try:
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')
    print("Connexion à mongoDB Atlas réussie.")
    db = client.sample_mflix
except ConnectionFailure as e:
    print(f"Error connecting to MongoDB Atlas: {e}")
    raise HTTPException(status_code=500, detail="Could not connect to MongoDB")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Weather Data API"}

@app.get("/weather_data")
async def get_all_weather_data(collection_name: str = "current_weather_clean"):
    """
    Retrieve all weather data from a specified collection.
    """
    try:
        collection = db[collection_name]
        data = []
        for doc in collection.find():
            doc['_id'] = str(doc['_id']) # Convert ObjectId to string for JSON serialization
            data.append(doc)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {e}")

@app.get("/weather_data/{item_id}")
async def get_weather_data_by_id(item_id: str, collection_name: str = "current_weather_clean"):
    """
    Retrieve weather data by its ID from a specified collection.
    """
    try:
        collection = db[collection_name]
        doc = collection.find_one({"_id": ObjectId(item_id)})
        if doc:
            doc['_id'] = str(doc['_id'])
            return doc
        raise HTTPException(status_code=404, detail="Item not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {e}")

@app.post("/weather_data")
async def add_weather_data(weather_entry: dict, collection_name: str = "current_weather_clean"):
    """
    Add a new weather data entry to a specified collection.
    """
    try:
        collection = db[collection_name]
        result = collection.insert_one(weather_entry)
        
        # Synchro Neo4j (Ajout)
        try:
            syncer = WeatherGraphSync()
            syncer.sync_data(weather_entry)
            syncer.close()
        except Exception as e:
            print(f"Warning: Neo4j sync failed: {e}")
            
        return {"message": "Weather data added successfully", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding data: {e}")

@app.put("/weather_data/{item_id}")
async def update_weather_data(item_id: str, weather_entry: dict, collection_name: str = "current_weather_clean"):
    """
    Update an existing weather data entry by its ID in a specified collection.
    """
    try:
        collection = db[collection_name]
        result = collection.update_one({"_id": ObjectId(item_id)}, {"$set": weather_entry})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Synchro Neo4j (Mise à jour)
        # On récupère le document complet mis à jour pour l'envoyer à Neo4j
        updated_doc = collection.find_one({"_id": ObjectId(item_id)})
        if updated_doc:
            try:
                syncer = WeatherGraphSync()
                syncer.sync_data(updated_doc)
                syncer.close()
            except Exception as e:
                print(f"Warning: Neo4j sync failed: {e}")

        return {"message": "Weather data updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating data: {e}")

@app.delete("/weather_data/{item_id}")
async def delete_weather_data(item_id: str, collection_name: str = "current_weather_clean"):
    """
    Delete a weather data entry by its ID from a specified collection.
    """
    try:
        collection = db[collection_name]
        
        # Récupérer le document avant suppression pour avoir la clé (time) pour Neo4j
        doc_to_delete = collection.find_one({"_id": ObjectId(item_id)})
        
        result = collection.delete_one({"_id": ObjectId(item_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Synchro Neo4j (Suppression)
        if doc_to_delete and 'time' in doc_to_delete:
            try:
                syncer = WeatherGraphSync()
                syncer.delete_data(doc_to_delete['time'])
                syncer.close()
            except Exception as e:
                print(f"Warning: Neo4j sync failed: {e}")

        return {"message": "Weather data deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting data: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
