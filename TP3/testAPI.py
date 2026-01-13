import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
if API_KEY:
    api = f"https://my.meteoblue.com/packages/current?lat=48.901020&lon=2.19&apikey={API_KEY}"
else:
    print("API_KEY introuvable dans le fichier .env. Veuillez le définir.")
    exit()

try:
    response = requests.get(api)
    response.raise_for_status()
    data = response.json()
    
    print(data)

except requests.exceptions.RequestException as erreur:
    print(f"Erreur lors de la récupération des données : {erreur}")
except ValueError as erreur:
    print(f"Erreur lors du décodage JSON : {erreur}")
