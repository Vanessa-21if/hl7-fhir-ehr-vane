from pymongo import MongoClient
from pymongo.server_api import ServerApi

def connect_to_mongodb(uri: str, db_name: str, collection_name: str):
    """
    Conexión básica a MongoDB para dispensación de medicamentos
    
    Args:
        uri: Cadena de conexión MongoDB
        db_name: Nombre de la base de datos
        collection_name: Nombre de la colección
    
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
        return collection.find_one(
            {"_id": patient_id},
            {  # Solo campos esenciales para dispensación
                "name": 1, 
                "identifier": 1
            }
        )
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
        ObjectId del registro creado o None en caso de error
    """
    try:
        # Estructura mínima FHIR para dispensación
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
                "value": med_data.get("quantity"),
                "unit": "unidades"
            },
            "daysSupply": {
                "value": med_data.get("daysSupply"),
                "unit": "días"
            },
            "dosageInstruction": [{
                "text": med_data.get("dosage")
            }],
            "timestamp": datetime.now()
        }
        
        result = med_collection.insert_one(dispense_record)
        return result.inserted_id
    except Exception as e:
        print(f"Error al registrar medicamento: {str(e)}")
        return None

# Ejemplo de uso simplificado
if __name__ == "__main__":
    # Configuración de conexión
    MONGODB_URI = "mongodb+srv://usuario:contraseña@cluster.mongodb.net/"
    DB_NAME = "DispensacionMedicamentos"
    
    try:
        # Conectar a colecciones
        patients = connect_to_mongodb(MONGODB_URI, DB_NAME, "pacientes")
        medications = connect_to_mongodb(MONGODB_URI, DB_NAME, "dispensaciones")
        
        # Ejemplo: Obtener datos básicos de paciente
        patient = get_patient_minimal_data(patients, "507f1f77bcf86cd799439011")
        
        # Ejemplo: Registrar dispensación
        if patient:
            med_data = {
                "medicationName": "Paracetamol 500mg",
                "quantity": 30,
                "daysSupply": 10,
                "dosage": "1 tableta cada 8 horas"
            }
            med_id = log_dispensed_medication(medications, patient["_id"], med_data)
            print(f"Medicamento dispensado con ID: {med_id}")
            
    except Exception as e:
        print(f"Error en el sistema: {str(e)}")
