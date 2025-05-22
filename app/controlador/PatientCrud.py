from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.patient import Patient
from fhir.resources.medicationdispense import MedicationDispense
from fhir.resources.medicationrequest import MedicationRequest
from datetime import datetime
import json

# Conexión a colecciones adicionales
patient_collection = connect_to_mongodb("SamplePatientService", "patients")
medication_collection = connect_to_mongodb("SamplePatientService", "medications")

def GetPatientById(patient_id: str):
    try:
        patient = patient_collection.find_one({"_id": ObjectId(patient_id)})
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        return f"notFound", None

def WritePatient(patient_dict: dict):
    try:
        pat = Patient.model_validate(patient_dict)
    except Exception as e:
        return f"errorValidating: {str(e)}", None
    validated_patient_json = pat.model_dump()
    result = patient_collection.insert_one(patient_dict)
    if result:
        inserted_id = str(result.inserted_id)
        return "success", inserted_id
    else:
        return "errorInserting", None

def GetPatientByIdentifier(patientSystem, patientValue):
    try:
        patient = patient_collection.find_one({"identifier.system": patientSystem, "identifier.value": patientValue})
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        return f"error: {str(e)}", None

def RegisterMedicationDispense(patient_id: str, medication_data: dict):
    """
    Registra la dispensación de un medicamento en la historia clínica del paciente
    según estándar FHIR MedicationDispense
    
    Args:
        patient_id: ID del paciente
        medication_data: {
            "medication": código/descripción del medicamento,
            "quantity": cantidad dispensada,
            "daysSupply": días de tratamiento,
            "performer": profesional que entrega,
            "prescriptionId": ID de la prescripción relacionada,
            "dosage": instrucciones de dosificación
        }
    """
    try:
        # Verificar que el paciente existe
        status, patient = GetPatientById(patient_id)
        if status != "success":
            return "patientNotFound", None
        
        # Crear recurso FHIR MedicationDispense
        dispense = {
            "resourceType": "MedicationDispense",
            "status": "completed",
            "medicationCodeableConcept": {
                "text": medication_data["medication"]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "whenHandedOver": datetime.now().isoformat(),
            "quantity": {
                "value": medication_data.get("quantity", 1)
            },
            "daysSupply": {
                "value": medication_data.get("daysSupply", 1)
            },
            "performer": [
                {
                    "actor": {
                        "display": medication_data.get("performer", "Unknown")
                    }
                }
            ],
            "authorizingPrescription": [
                {
                    "reference": f"MedicationRequest/{medication_data.get('prescriptionId', '')}"
                }
            ],
            "dosageInstruction": [
                {
                    "text": medication_data.get("dosage", "As prescribed")
                }
            ]
        }
        
        # Validar y guardar
        try:
            md = MedicationDispense.model_validate(dispense)
            result = medication_collection.insert_one(dispense)
            return "success", str(result.inserted_id)
        except Exception as e:
            return f"errorValidating: {str(e)}", None
            
    except Exception as e:
        return f"error: {str(e)}", None

def GetPatientMedications(patient_id: str):
    """
    Obtiene todos los medicamentos dispensados para un paciente
    """
    try:
        medications = list(medication_collection.find({
            "subject.reference": f"Patient/{patient_id}"
        }))
        
        for med in medications:
            med["_id"] = str(med["_id"])
        
        return "success", medications
    except Exception as e:
        return f"error: {str(e)}", None
