from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.patient import Patient
from fhir.resources.medicationdispense import MedicationDispense
from datetime import datetime

# Conexión a colecciones
patient_collection = connect_to_mongodb("SamplePatientService", "patients")
medication_collection = connect_to_mongodb("SamplePatientService", "medications")

def GetPatientById(patient_id: str):
    """Obtiene un paciente por su ID (versión simplificada)"""
    try:
        patient = patient_collection.find_one(
            {"_id": ObjectId(patient_id)},
            {"name": 1, "identifier": 1}  # Solo campos esenciales
        )
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        return f"error: {str(e)}", None

def WritePatient(patient_dict: dict):
    """Crea un nuevo paciente con datos mínimos"""
    try:
        # Validar estructura FHIR básica del paciente
        required_fields = ["name", "identifier"]
        for field in required_fields:
            if field not in patient_dict:
                return f"missingField: {field}", None
        
        pat = Patient.model_validate(patient_dict)
        validated_patient = pat.model_dump()
        
        # Solo metadatos esenciales
        validated_patient["createdAt"] = datetime.now()
        
        # Insertar en MongoDB
        result = patient_collection.insert_one(validated_patient)
        if result.inserted_id:
            return "success", str(result.inserted_id)
        return "errorInserting", None
    except Exception as e:
        return f"errorValidating: {str(e)}", None

def RegisterMedicationDispense(patient_id: str, medication_data: dict):
    """Registra una dispensación de medicamento (versión simplificada)"""
    try:
        # Verificación básica del paciente
        status, patient = GetPatientById(patient_id)
        if status != "success":
            return "patientNotFound", None
        
        # Validar campos requeridos
        required_fields = ["medicationName", "quantity", "daysSupply", "dosage"]
        for field in required_fields:
            if field not in medication_data:
                return f"missingField: {field}", None

        # Crear recurso FHIR MedicationDispense mínimo
        dispense = {
            "resourceType": "MedicationDispense",
            "status": "completed",
            "medicationCodeableConcept": {
                "text": medication_data["medicationName"]
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "quantity": {
                "value": float(medication_data["quantity"]),
                "unit": "unidades"
            },
            "daysSupply": {
                "value": float(medication_data["daysSupply"]),
                "unit": "días"
            },
            "dosageInstruction": [
                {
                    "text": medication_data["dosage"]
                }
            ],
            "createdAt": datetime.now()
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
    """Obtiene medicamentos dispensados a un paciente (versión simplificada)"""
    try:
        medications = list(medication_collection.find(
            {"subject.reference": f"Patient/{patient_id}"},
            {  # Solo campos esenciales
                "medicationCodeableConcept.text": 1,
                "quantity": 1,
                "daysSupply": 1,
                "dosageInstruction": 1,
                "createdAt": 1
            }
        ).sort("createdAt", -1))  # Ordenar por fecha descendente
        
        for med in medications:
            med["_id"] = str(med["_id"])
            if "createdAt" in med:
                med["createdAt"] = med["createdAt"].isoformat()
        
        return "success", medications
    except Exception as e:
        return f"error: {str(e)}", None
