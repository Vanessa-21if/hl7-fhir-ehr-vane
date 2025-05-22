import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # Carga variables del archivo .env

def connect_to_mongo_db():
    load_dotenv()
    mongodb_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongodb_uri)
    return client
    MONGO_URI="mongodb+srv://21vanessaaa:VANEifmer2025@sampleinformationservic.ceivw.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"
    API_PORT=8000
    ALLOWED_ORIGINS="https://hl7-patient-write-vanessa.onrender.com,http://localhost:3000"

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
