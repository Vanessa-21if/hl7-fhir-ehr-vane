import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from typing import Optional
from fhir.resources.patient import Patient
from fhir.resources.medicationdispense import MedicationDispense
from pydantic import ValidationError
import os
from dotenv import load_dotenv
from src.connection import connect_to_mongodb  


load_dotenv()

class ClinicalRecordSystem:
    """Sistema de registro clínico para cumplir la historia de usuario"""

    def __init__(self):
        """Inicializa conexión a MongoDB"""
            def connect_to_mongo_db():
            load_dotenv()
            mongodb_uri = os.getenv('MONGO_URI')
            client = MongoClient(mongodb_uri)
            return client
        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("DB_NAME", "SamplePatientService")
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        self.db = self.client[self.db_name]
        
        # Colecciones
        self.patients = self.db['patients']
        self.medications = self.db['medications']
        
        self._verify_connection()

    def _verify_connection(self):
        """Verifica que la conexión a MongoDB esté activa"""
        try:
            self.client.admin.command('ping')
            print("✅ Conexión a MongoDB establecida correctamente")
        except Exception as e:
            print(f"❌ Error de conexión a MongoDB: {e}")
            raise

    def register_patient(self, patient_data: dict) -> Optional[str]:
        """
        Registra un nuevo paciente en el sistema
        Cumple con el estándar FHIR
        
        Args:
            patient_data: Diccionario con datos del paciente en formato FHIR
            
        Returns:
            ID del paciente registrado o None si falla
        """
        try:
            # Validación FHIR
            patient = Patient.model_validate(patient_data)
            patient_dict = patient.model_dump()
            
            # Metadatos adicionales
            patient_dict['createdAt'] = datetime.utcnow()
            patient_dict['updatedAt'] = datetime.utcnow()
            
            # Insertar en MongoDB
            result = self.patients.insert_one(patient_dict)
            return str(result.inserted_id)
            
        except ValidationError as e:
            print(f"❌ Error de validación FHIR: {e}")
            return None
        except Exception as e:
            print(f"❌ Error al registrar paciente: {e}")
            return None

    def record_medication(self, patient_id: str, medication_data: dict) -> Optional[str]:
        """
        Registra un medicamento en la historia clínica del paciente
        Cumple con la historia de usuario requerida
        
        Args:
            patient_id: ID del paciente
            medication_data: Datos del medicamento a registrar
            
        Returns:
            ID del registro de medicamento o None si falla
        """
        try:
            # Verificar que el paciente existe
            if not self.patients.find_one({"_id": patient_id}):
                print("⚠️ El paciente no existe en el sistema")
                return None
            
            # Crear recurso FHIR MedicationDispense
            medication_data.update({
                "resourceType": "MedicationDispense",
                "status": "completed",
                "subject": {
                    "reference": f"Patient/{patient_id}",
                    "type": "Patient"
                },
                "whenHandedOver": datetime.utcnow().isoformat()
            })
            
            medication = MedicationDispense.model_validate(medication_data)
            med_dict = medication.model_dump()
            
            # Metadatos para trazabilidad
            med_dict['createdAt'] = datetime.utcnow()
            med_dict['updatedAt'] = datetime.utcnow()
            
            # Insertar en MongoDB
            result = self.medications.insert_one(med_dict)
            return str(result.inserted_id)
            
        except ValidationError as e:
            print(f"❌ Error de validación FHIR: {e}")
            return None
        except Exception as e:
            print(f"❌ Error al registrar medicamento: {e}")
            return None

    def close(self):
        """Cierra la conexión a MongoDB"""
        self.client.close()


# Ejemplo de uso que cumple con la historia de usuario
if __name__ == "__main__":
    # Configuración
    system = ClinicalRecordSystem()
    
    try:
        # 1. Registrar paciente (paso previo necesario)
        patient_data = {
            "resourceType": "Patient",
            "identifier": [{
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "NN"
                    }],
                    "text": "Cédula"
                },
                "system": "http://cedula",
                "value": "1020713756"
            }],
            "name": [{
                "use": "official",
                "family": "Duarte",
                "given": ["Mario", "Enrique"]
            }],
            "gender": "male",
            "birthDate": "1986-02-25"
        }
        
        patient_id = system.register_patient(patient_data)
        print(f"ID Paciente: {patient_id}")
        
        # 2. Registrar medicamento (historia de usuario principal)
        if patient_id:
            medication_data = {
                "medicationCodeableConcept": {
                    "text": "Amoxicilina 500mg",
                    "coding": [{
                        "system": "http://snomed.info/sct",
                        "code": "372665000"
                    }]
                },
                "quantity": {
                    "value": 20,
                    "unit": "tabletas"
                },
                "daysSupply": {
                    "value": 10,
                    "unit": "días"
                },
                "dosageInstruction": [{
                    "text": "Tomar 1 tableta cada 12 horas"
                }],
                "performer": [{
                    "actor": {
                        "display": "Dr. Rodríguez"
                    }
                }]
            }
            
            med_id = system.record_medication(patient_id, medication_data)
            
            if med_id:
                print(f"✅ Medicamento registrado correctamente (ID: {med_id})")
                print("Historia clínica actualizada con el tratamiento farmacéutico")
            else:
                print("❌ No se pudo registrar el medicamento")
                
    finally:
        system.close()
        
