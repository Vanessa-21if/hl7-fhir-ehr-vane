import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from typing import List, Dict, Optional
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

class MongoDBHelper:
    """Clase mejorada para manejar operaciones de MongoDB para el sistema de salud"""
    
    def __init__(self):
        """Inicializa la conexión a MongoDB usando variables de entorno"""
        self.uri = os.getenv("MONGO_URI", "mongodb+srv://default:password@cluster.mongodb.net")
        self.db_name = os.getenv("DB_NAME", "SamplePatientService")
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        self.db = self.client[self.db_name]
        
        # Colecciones
        self.patients = self.db['patients']
        self.medications = self.db['medications']
        
        self._test_connection()

    def _test_connection(self):
        """Verifica que la conexión a MongoDB esté activa"""
        try:
            self.client.admin.command('ping')
            print("✅ Conexión exitosa a MongoDB")
        except Exception as e:
            print(f"❌ Error de conexión a MongoDB: {e}")
            raise

    # ===== OPERACIONES PARA PACIENTES =====
    def get_all_patients(self, limit: int = 100) -> List[Dict]:
        """Obtiene todos los pacientes con un límite opcional"""
        try:
            return list(self.patients.find().limit(limit))
        except Exception as e:
            print(f"Error al obtener pacientes: {e}")
            return []

    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """Obtiene un paciente por su ID"""
        try:
            patient = self.patients.find_one({"_id": ObjectId(patient_id)})
            return self._format_document(patient)
        except Exception as e:
            print(f"Error buscando paciente por ID: {e}")
            return None

    def search_patients(self, query: Dict) -> List[Dict]:
        """Busca pacientes según criterios personalizados"""
        try:
            return [self._format_document(p) for p in self.patients.find(query)]
        except Exception as e:
            print(f"Error en búsqueda de pacientes: {e}")
            return []

    # ===== OPERACIONES PARA MEDICAMENTOS =====
    def get_patient_medications(self, patient_id: str) -> List[Dict]:
        """Obtiene todos los medicamentos de un paciente"""
        try:
            meds = self.medications.find(
                {"subject.reference": f"Patient/{patient_id}"}
            ).sort("whenHandedOver", -1)
            
            return [self._format_document(m) for m in meds]
        except Exception as e:
            print(f"Error obteniendo medicamentos: {e}")
            return []

    def add_medication(self, patient_id: str, medication_data: Dict) -> Optional[str]:
        """Agrega un medicamento a la historia clínica"""
        try:
            # Validar que exista el paciente
            if not self.get_patient_by_id(patient_id):
                raise ValueError("Paciente no encontrado")
                
            # Estructura FHIR básica
            medication = {
                "resourceType": "MedicationDispense",
                "status": "completed",
                "subject": {
                    "reference": f"Patient/{patient_id}"
                },
                **medication_data,
                "recorded": datetime.utcnow()
            }
            
            result = self.medications.insert_one(medication)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error agregando medicamento: {e}")
            return None

    # ===== MÉTODOS UTILITARIOS =====
    @staticmethod
    def _format_document(doc: Dict) -> Dict:
        """Formatea documentos MongoDB para respuesta API"""
        if not doc:
            return None
            
        formatted = doc.copy()
        if '_id' in formatted:
            formatted['id'] = str(formatted.pop('_id'))
        return formatted

    def close(self):
        """Cierra la conexión a MongoDB"""
        self.client.close()


# Ejemplo de uso mejorado
if __name__ == "__main__":
    # Configuración desde variables de entorno
    helper = MongoDBHelper()
    
    try:
        print("\n=== Sistema de Historia Clínica Electrónica ===")
        
        # 1. Obtener todos los pacientes
        patients = helper.get_all_patients(limit=5)
        print(f"\n📋 Total pacientes encontrados: {len(patients)}")
        
        for idx, patient in enumerate(patients, 1):
            print(f"\nPaciente #{idx}:")
            print(f"  ID: {patient.get('id')}")
            print(f"  Nombre: {patient.get('name', [{}])[0].get('given', [''])[0]} {patient.get('name', [{}])[0].get('family', '')}")
            print(f"  Género: {patient.get('gender', 'Desconocido')}")
            
            # 2. Obtener medicamentos para cada paciente
            meds = helper.get_patient_medications(patient['id'])
            print(f"  💊 Medicamentos recetados: {len(meds)}")
            
            for med in meds[:2]:  # Mostrar primeros 2 medicamentos
                print(f"    - {med.get('medicationCodeableConcept', {}).get('text', 'Sin nombre')}")
                
    finally:
        helper.close()
