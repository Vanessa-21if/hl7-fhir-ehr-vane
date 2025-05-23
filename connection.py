import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # Carga variables del archivo .env

def get_db_connection():
    """Establece conexión a la base de datos"""
    client = MongoClient(os.getenv("MONGO_URI"))
    db_name = os.getenv("MONGO_URI").split('/')[-1].split('?')[0]
    return client[db_name]

# Conexión a las colecciones
def get_patients_collection():
    db = get_db_connection()
    return db["patients"]

def get_medications_collection():
    db = get_db_connection()
    return db["medications"]
