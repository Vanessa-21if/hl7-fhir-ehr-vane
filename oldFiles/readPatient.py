import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from typing import List, Dict, Optional, Union
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import os
from fhir.resources.patient import Patient
from fhir.resources.medicationdispense import MedicationDispense
from pydantic import ValidationError
from connection import connect_to_mongodb  

class ClinicalRecordReader:
    """Sistema de lectura para historia clínica electrónica que cumple con la historia de usuario"""
    
    def __init__(self):
        """Inicializa la conexión a MongoDB"""
        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("DB_NAME", "SampleInformationtService")
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))
        self.db = self.client[self.db_name]
        
        # Colecciones FHIR
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

    def _format_document(self, doc: Dict, resource_type: str = None) -> Optional[Dict]:
        """Formatea documentos MongoDB y valida estructura FHIR"""
        if not doc:
            return None
            
        try:
            # Convertir ObjectId a string
            doc['id'] = str(doc.pop('_id'))
            
            # Validar estructura FHIR si se especifica
            if resource_type == "Patient":
                Patient.model_validate(doc)
            elif resource_type == "MedicationDispense":
                MedicationDispense.model_validate(doc)
                
            return doc
        except ValidationError as e:
            print(f"⚠️ Documento no cumple con FHIR: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Error formateando documento: {e}")
            return None

    # ===== OPERACIONES PARA PACIENTES =====
    def get_patient(self, patient_id: str) -> Optional[Dict]:
        """Obtiene un paciente por ID con validación FHIR"""
        try:
            patient = self.patients.find_one({"_id": ObjectId(patient_id)})
            return self._format_document(patient, "Patient")
        except Exception as e:
            print(f"❌ Error obteniendo paciente: {e}")
            return None

    def search_patients(self, search_criteria: Dict) -> List[Dict]:
        """Busca pacientes según criterios con validación FHIR"""
        try:
            patients = list(self.patients.find(search_criteria))
            return [p for p in (
                self._format_document(patient, "Patient") 
                for patient in patients
            ) if p is not None]
        except Exception as e:
            print(f"❌ Error buscando pacientes: {e}")
            return []

    # ===== OPERACIONES PARA MEDICAMENTOS =====
    def get_patient_medications(
        self, 
        patient_id: str,
        include_patient: bool = False
    ) -> Union[Dict, List[Dict]]:
        """
        Obtiene los medicamentos de un paciente cumpliendo con la historia de usuario
        
        Args:
            patient_id: ID del paciente
            include_patient: Si True, incluye datos del paciente en la respuesta
            
        Returns:
            Dict con paciente y medicamentos si include_patient=True
            List[Dict] con solo medicamentos si include_patient=False
        """
        try:
            # Validar que el paciente existe
            patient = self.get_patient(patient_id)
            if not patient:
                return {"error": "Paciente no encontrado"} if include_patient else []
            
            # Obtener medicamentos ordenados por fecha descendente
            medications = list(self.medications.find(
                {"subject.reference": f"Patient/{patient_id}"}
            ).sort("whenHandedOver", -1))
            
            # Validar y formatear medicamentos
            formatted_meds = [
                self._format_document(med, "MedicationDispense") 
                for med in medications
            ]
            valid_medications = [m for m in formatted_meds if m is not None]
            
            if include_patient:
                return {
                    "patient": patient,
                    "medications": valid_medications,
                    "medication_count": len(valid_medications),
                    "last_medication_date": (
                        valid_medications[0]["whenHandedOver"] 
                        if valid_medications else None
                    )
                }
            return valid_medications
            
        except Exception as e:
            print(f"❌ Error obteniendo medicamentos: {e}")
            return {"error": str(e)} if include_patient else []

    def get_medication_by_id(self, medication_id: str) -> Optional[Dict]:
        """Obtiene un medicamento por ID con validación FHIR"""
        try:
            medication = self.medications.find_one({"_id": ObjectId(medication_id)})
            return self._format_document(medication, "MedicationDispense")
        except Exception as e:
            print(f"❌ Error obteniendo medicamento: {e}")
            return None

    # ===== MÉTODOS PARA REPORTES =====
    def get_medications_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Dict]:
        """Obtiene medicamentos dispensados en un rango de fechas"""
        try:
            medications = list(self.medications.find({
                "whenHandedOver": {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            }).sort("whenHandedOver", -1))
            
            return [
                m for m in (
                    self._format_document(med, "MedicationDispense") 
                    for med in medications
                ) if m is not None
            ]
        except Exception as e:
            print(f"❌ Error obteniendo medicamentos por fecha: {e}")
            return []

    def close(self):
        """Cierra la conexión a MongoDB"""
        self.client.close()


# Ejemplo de uso que cumple con la historia de usuario
if __name__ == "__main__":
    print("=== Sistema de Lectura de Historia Clínica ===")
    
    # Configuración
    reader = ClinicalRecordReader()
    
    try:
        # 1. Obtener un paciente específico con sus medicamentos
        patient_id = "507f1f77bcf86cd799439011"  # Reemplazar con ID real
        clinical_record = reader.get_patient_medications(patient_id, include_patient=True)
        
        if isinstance(clinical_record, dict) and "error" not in clinical_record:
            print(f"\n📋 Historia clínica para: {clinical_record['patient']['name'][0]['given'][0]} {clinical_record['patient']['name'][0]['family']}")
            print(f"📅 Última medicación: {clinical_record.get('last_medication_date', 'N/A')}")
            print(f"💊 Total medicamentos registrados: {clinical_record['medication_count']}")
            
            # Mostrar últimos 3 medicamentos
            print("\nÚltimos medicamentos:")
            for med in clinical_record['medications'][:3]:
                print(f"- {med['medicationCodeableConcept']['text']} ({med.get('whenHandedOver', 'sin fecha')})")
                print(f"  Dosificación: {med['dosageInstruction'][0]['text']}")
                print(f"  Cantidad: {med['quantity']['value']} {med['quantity']['unit']}")
        
        # 2. Ejemplo de reporte mensual de medicamentos
        print("\n📊 Reporte de medicamentos (ejemplo):")
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        monthly_meds = reader.get_medications_by_date_range(start_date, end_date)
        
        print(f"Total medicamentos en enero 2023: {len(monthly_meds)}")
        
    finally:
        reader.close()
