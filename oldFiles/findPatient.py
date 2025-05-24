from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from datetime import datetime

def connect_to_mongodb(db_name: str, collection_name: str, uri: str):
    """
    Conexión básica a MongoDB para dispensación de medicamentos

    Args:
        db_name: Nombre de la base de datos
        collection_name: Nombre de la colección
        uri: Cadena de conexión MongoDB
    
    Returns:
        Objeto de colección MongoDB
    """
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        return client[db_name][collection_name]
    except Exception as e:
        print(f"Error de conexión: {str(e)}")
        raise

def get_patient_minimal_data(collection, patient_id: str):
    """
    Obtiene datos mínimos del paciente necesarios para dispensación
    
    Args:
        collection: Colección MongoDB
        patient_id: ID del paciente
    
    Returns:
        Dict con datos básicos del paciente o None si no se encuentra
    """
    try:
        patient = collection.find_one(
            {"_id": ObjectId(patient_id)},
            {  # Solo campos esenciales para dispensación
                "name": 1,
                "identifier": 1
            }
        )
        if patient:
            patient["_id"] = str(patient["_id"])
        return patient
    except Exception as e:
        print(f"Error en búsqueda de paciente: {str(e)}")
        return None

def log_dispensed_medication(med_collection, patient_id: str, med_data: dict):
    """
    Registra una dispensación de medicamento
    
    Args:
        med_collection: Colección de medicamentos
        patient_id: ID del paciente
        med_data: Datos del medicamento dispensado
    
    Returns:
        String con ObjectId del registro creado o None en caso de error
    """
    try:
        dispense_record = {
            "resourceType": "MedicationDispense",
            "status": "completed",
            "medicationCodeableConcept": {
                "text": med_data.get("medicationName")
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "quantity": {
                "value": float(med_data.get("quantity")),
                "unit": "unidades"
            },
            "daysSupply": {
                "value": float(med_data.get("daysSupply")),
                "unit": "días"
            },
            "dosageInstruction": [{
                "text": med_data.get("dosage")
            }],
            "createdAt": datetime.now()
        }
        
        result = med_collection.insert_one(dispense_record)
        if result.inserted_id:
            return str(result.inserted_id)
        return None
    except Exception as e:
        print(f"Error al registrar medicamento: {str(e)}")
        return None


# Ejemplo de uso simplificado
if __name__ == "__main__":
    import os

    # Configuración de conexión desde variable de entorno o fija
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://usuario:contraseña@cluster.mongodb.net/")
    DB_NAME = "SamplePatientService"  # Para coincidir con patientcrud.py
    
    try:
        patients = connect_to_mongodb(DB_NAME, "patient", MONGODB_URI)
        medications = connect_to_mongodb(DB_NAME, "medications", MONGODB_URI)
        
        # Ejemplo: Obtener datos básicos de paciente
        patient_id = "507f1f77bcf86cd799439011"  # Cambia por uno real
        patient = get_patient_minimal_data(patients, patient_id)
        
        # Ejemplo: Registrar dispensación
        if patient:
            med_data = {
                "medicationName": "Paracetamol 500mg",
                "quantity": 30,
                "daysSupply": 10,
                "dosage": "1 tableta cada 8 horas"
            }
            med_id = log_dispensed_medication(medications, patient_id, med_data)
            print(f"Medicamento dispensado con ID: {med_id}")
        else:
            print("Paciente no encontrado")
            
    except Exception as e:
        print(f"Error en el sistema: {str(e)}")
