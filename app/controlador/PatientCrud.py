from connection import connect_to_mongodb
from bson import ObjectId
from datetime import datetime

# Conexión a colecciones MongoDB
patient_collection = connect_to_mongodb("SamplePatientService", "patient")
medication_collection = connect_to_mongodb("SamplePatientService", "medications")

def GetPatientById(patient_id: str):
    """Obtiene un paciente por su ID (simplificado)."""
    try:
        patient = patient_collection.find_one(
            {"_id": ObjectId(patient_id)},
            {"document": 1}  # Solo documento (ID del paciente)
        )
        if patient:
            patient["_id"] = str(patient["_id"])
            return "success", patient
        return "notFound", None
    except Exception as e:
        return f"error: {str(e)}", None

def WritePatient(patient_data: dict):
    """
    Crea un nuevo paciente con datos mínimos (documento).
    Se espera patient_data = {"document": "número_documento"}
    """
    try:
        document = patient_data.get("document")
        if not document:
            return "missingField: document", None
        
        # Verificar si ya existe paciente con ese documento
        existing = patient_collection.find_one({"document": document})
        if existing:
            return "success", str(existing["_id"])
        
        new_patient = {
            "document": document,
            "createdAt": datetime.now()
        }
        result = patient_collection.insert_one(new_patient)
        if result.inserted_id:
            return "success", str(result.inserted_id)
        return "errorInserting", None
    except Exception as e:
        return f"error: {str(e)}", None

def RegisterMedicationDispense(patient_id: str, medication_data: dict):
    """
    Registra una dispensación de medicamento para un paciente.
    medication_data debe contener:
      - medicationName
      - quantity
      - daysSupply
      - dosage
    """
    try:
        # Verificar paciente existe
        status, patient = GetPatientById(patient_id)
        if status != "success":
            return "patientNotFound", None
        
        # Validar campos requeridos
        for field in ["medicationName", "quantity", "daysSupply", "dosage"]:
            if field not in medication_data:
                return f"missingField: {field}", None
        
        dispense_record = {
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
                {"text": medication_data["dosage"]}
            ],
            "createdAt": datetime.now()
        }
        
        result = medication_collection.insert_one(dispense_record)
        if result.inserted_id:
            return "success", str(result.inserted_id)
        return "errorInserting", None
    except Exception as e:
        return f"error: {str(e)}", None

def GetPatientMedications(patient_id: str):
    """Obtiene historial de medicamentos dispensados a un paciente."""
    try:
        meds_cursor = medication_collection.find(
            {"subject.reference": f"Patient/{patient_id}"},
            {
                "medicationCodeableConcept.text": 1,
                "quantity": 1,
                "daysSupply": 1,
                "dosageInstruction": 1,
                "createdAt": 1
            }
        ).sort("createdAt", -1)
        
        medications = []
        for med in meds_cursor:
            med["_id"] = str(med["_id"])
            if "createdAt" in med and med["createdAt"]:
                med["createdAt"] = med["createdAt"].isoformat()
            medications.append(med)
        
        return "success", medications
    except Exception as e:
        return f"error: {str(e)}", None
