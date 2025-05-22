from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.patient import Patient
from fhir.resources.medicationdispense import MedicationDispense
from datetime import datetime
import json

# Conexión a colecciones
patient_collection = connect_to_mongodb("SamplePatientService", "patients")
medication_collection = connect_to_mongodb("SamplePatientService", "medications")

def GetPatientById(patient_id: str):
    """Obtiene un paciente por su ID"""
    try:
        patient = patient_collection.find_one({"_id": ObjectId(patient_id)})
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        return f"error: {str(e)}", None

def WritePatient(patient_dict: dict):
    """Crea un nuevo paciente en la base de datos"""
    try:
        # Validar estructura FHIR del paciente
        pat = Patient.model_validate(patient_dict)
        validated_patient = pat.model_dump()
        
        # Añadir metadatos adicionales
        validated_patient["createdAt"] = datetime.now()
        validated_patient["updatedAt"] = datetime.now()
        
        # Insertar en MongoDB
        result = patient_collection.insert_one(validated_patient)
        if result.inserted_id:
            return "success", str(result.inserted_id)
        return "errorInserting", None
    except Exception as e:
        return f"errorValidating: {str(e)}", None

def GetPatientByIdentifier(patientSystem: str, patientValue: str):
    """Busca un paciente por su identificador"""
    try:
        patient = patient_collection.find_one({
            "identifier": {
                "$elemMatch": {
                    "system": patientSystem,
                    "value": patientValue
                }
            }
        })
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        return f"error: {str(e)}", None

def RegisterMedicationDispense(patient_id: str, medication_data: dict):
    """Registra un medicamento para un paciente"""
    try:
        # Verificar que el paciente existe
        status, patient = GetPatientById(patient_id)
        if status != "success":
            return "patientNotFound", None
        
        # Crear recurso FHIR MedicationDispense completo
        dispense = {
            "resourceType": "MedicationDispense",
            "status": "completed",
            "medicationCodeableConcept": {
                "text": medication_data.get("medication", "")
            },
            "subject": {
                "reference": f"Patient/{patient_id}",
                "display": f"{patient['name'][0]['given'][0]} {patient['name'][0]['family']}"
            },
            "whenHandedOver": datetime.now().isoformat(),
            "quantity": {
                "value": float(medication_data.get("quantity", 1)),
                "unit": medication_data.get("unit", "unit")
            },
            "daysSupply": {
                "value": float(medication_data.get("daysSupply", 1)),
                "unit": "days"
            },
            "performer": [
                {
                    "actor": {
                        "display": medication_data.get("performer", "Unknown"),
                        "type": "Practitioner"
                    }
                }
            ],
            "dosageInstruction": [
                {
                    "text": medication_data.get("dosage", "As prescribed"),
                    "timing": {
                        "repeat": {
                            "frequency": 1,
                            "period": 1,
                            "periodUnit": "d"
                        }
                    }
                }
            ],
            "note": [
                {
                    "text": medication_data.get("notes", "")
                }
            ],
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }

        # Validar estructura FHIR
        md = MedicationDispense.model_validate(dispense)
        validated_dispense = md.model_dump()
        
        # Insertar en MongoDB
        result = medication_collection.insert_one(validated_dispense)
        if result.inserted_id:
            return "success", str(result.inserted_id)
        return "errorInserting", None
        
    except Exception as e:
        return f"error: {str(e)}", None

def GetPatientMedications(patient_id: str):
    """Obtiene todos los medicamentos de un paciente"""
    try:
        # Verificar que el paciente existe primero
        status, _ = GetPatientById(patient_id)
        if status != "success":
            return "patientNotFound", None
            
        medications = list(medication_collection.find({
            "subject.reference": f"Patient/{patient_id}"
        }).sort("whenHandedOver", -1))  # Ordenar por fecha descendente
        
        for med in medications:
            med["_id"] = str(med["_id"])
            # Convertir fechas a string para respuesta JSON
            if "whenHandedOver" in med:
                med["whenHandedOver"] = med["whenHandedOver"].isoformat()
            if "createdAt" in med:
                med["createdAt"] = med["createdAt"].isoformat()
            if "updatedAt" in med:
                med["updatedAt"] = med["updatedAt"].isoformat()
        
        return "success", medications
    except Exception as e:
        return f"error: {str(e)}", None
