from pymongo import MongoClient
from pymongo.server_api import ServerApi
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from src.connection import connect_to_mongodb  

class MongoDBConnector:
    
    def __init__(self, uri: str, db_name: str):
        
            def connect_to_mongo_db():
    load_dotenv()
    mongodb_uri = os.getenv('MONGO_URI')
    client = MongoClient(mongodb_uri)
    return client
         
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client[db_name]
        
        # Conexiones a las colecciones
        self.patients = self.db['patients']
        self.medications = self.db['medications']
        
        # Verificar conexión
        try:
            self.client.admin.command('ping')
            print("Conexión exitosa a MongoDB")
        except Exception as e:
            print(f"Error de conexión: {e}")

    # === Operaciones para Pacientes ===
    def find_patient_by_id(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Busca un paciente por su ID"""
        try:
            return self.patients.find_one({"_id": ObjectId(patient_id)})
        except Exception as e:
            print(f"Error buscando paciente por ID: {e}")
            return None

    def find_patient_by_identifier(self, identifier_type: str, identifier_value: str) -> Optional[Dict[str, Any]]:
        """Busca paciente por identificador (tipo y valor)"""
        try:
            query = {
                "identifier": {
                    "$elemMatch": {
                        "type.text": identifier_type,
                        "value": identifier_value
                    }
                }
            }
            return self.patients.find_one(query)
        except Exception as e:
            print(f"Error buscando por identificador: {e}")
            return None

    def insert_patient(self, patient_data: Dict[str, Any]) -> Optional[str]:
        """Inserta un nuevo paciente con metadatos"""
        try:
            patient_data['createdAt'] = datetime.utcnow()
            patient_data['updatedAt'] = datetime.utcnow()
            result = self.patients.insert_one(patient_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error insertando paciente: {e}")
            return None

    # === Operaciones para Medicamentos ===
    def find_medications_by_patient(self, patient_id: str) -> list:
        """Busca todos los medicamentos de un paciente"""
        try:
            return list(self.medications.find(
                {"subject.reference": f"Patient/{patient_id}"}
            ).sort("whenHandedOver", -1))
        except Exception as e:
            print(f"Error buscando medicamentos: {e}")
            return []

    def insert_medication(self, patient_id: str, medication_data: Dict[str, Any]) -> Optional[str]:
        """Registra un nuevo medicamento para un paciente"""
        try:
            # Validación básica
            if not self.find_patient_by_id(patient_id):
                print("Paciente no encontrado")
                return None
                
            medication_data['subject'] = {
                "reference": f"Patient/{patient_id}",
                "type": "Patient"
            }
            medication_data['whenHandedOver'] = datetime.utcnow()
            medication_data['createdAt'] = datetime.utcnow()
            
            result = self.medications.insert_one(medication_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error insertando medicamento: {e}")
            return None

    # === Métodos de utilidad ===
    @staticmethod
    def format_patient_output(patient: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea la salida del paciente para respuesta API"""
        if not patient:
            return None
            
        formatted = patient.copy()
        formatted['_id'] = str(formatted['_id'])
        return formatted

    def close_connection(self):
        """Cierra la conexión a MongoDB"""
        self.client.close()


# Ejemplo de uso mejorado
if __name__ == "__main__":
    # Configuración (debería venir de variables de entorno en producción)
    URI = "mongodb+srv://21vanessaaa:VANEifmer2025@sampleinformationservic.ceivw.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"
    DB_NAME = "SamplePatientService"
    
    # Crear instancia del conector
    mongo = MongoDBConnector(URI, DB_NAME)
    
    try:
        # 1. Buscar paciente por identificador
        patient = mongo.find_patient_by_identifier("cc", "1020713756")
        
        if patient:
            print("\nPaciente encontrado:")
            print(f"ID: {patient['_id']}")
            print(f"Nombre: {patient['name'][0]['given'][0]} {patient['name'][0]['family']}")
            
            # 2. Si existe, buscar sus medicamentos
            patient_id = str(patient['_id'])
            meds = mongo.find_medications_by_patient(patient_id)
            
            print(f"\nMedicamentos ({len(meds)}):")
            for med in meds:
                print(f"- {med['medicationCodeableConcept']['text']}")
        else:
            print("Paciente no encontrado")
            
    finally:
        # Siempre cerrar la conexión
        mongo.close_connection()
