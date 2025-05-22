from connection import connect_to_mongodb
from bson import ObjectId
from fhir.resources.patients import patients
from fhir.resources.medicationsdispense import medicationsDispense
from datetime import datetime
import json

# Conexión a colecciones
patients_collection = connect_to_mongodb("SampleInformationService", "patientss")
medications_collection = connect_to_mongodb("SampleInformationService", "medicationss")

def GetpatientsById(patients_id: str):
    """Obtiene un paciente por su ID"""
    try:
        patients = patients_collection.find_one({"_id": ObjectId(patients_id)})
        if patients:
            patients["_id"] = str(patients["_id"])
            return "success", patients
        return "notFound", None
    except Exception as e:
        return f"error: {str(e)}", None

def Writepatients(patients_dict: dict):
    """Crea un nuevo paciente en la base de datos"""
    try:
        # Validar estructura FHIR del paciente
        pat = patients.model_validate(patients_dict)
        validated_patients = pat.model_dump()
        
        # Añadir metadatos adicionales
        validated_patients["createdAt"] = datetime.now()
        validated_patients["updatedAt"] = datetime.now()
        
        # Insertar en MongoDB
        result = patients_collection.insert_one(validated_patients)
        if result.inserted_id:
            return "success", str(result.inserted_id)
        return "errorInserting", None
    except Exception as e:
        return f"errorValidating: {str(e)}", None

def GetpatientsByIdentifier(patientsSystem: str, patientsValue: str):
    """Busca un paciente por su identificador"""
    try:
        patients = patients_collection.find_one({
            "identifier": {
                "$elemMatch": {
                    "system": patientsSystem,
                    "value": patientsValue
                }
            }
        })
        if patients:
            patients["_id"] = str(patients["_id"])
            return "success", patients
        return "notFound", None
    except Exception as e:
        return f"error: {str(e)}", None

def RegistermedicationsDispense(patients_id: str, medications_data: dict):
    """Registra un medicamento para un paciente"""
    try:
        # Verificar que el paciente existe
        status, patients = GetpatientsById(patients_id)
        if status != "success":
            return "patientsNotFound", None
        
        # Crear recurso FHIR medicationsDispense completo
        dispense = {
            "resourceType": "medicationsDispense",
            "status": "completed",
            "medicationsCodeableConcept": {
                "text": medications_data.get("medications", "")
            },
            "subject": {
                "reference": f"patients/{patients_id}",
                "display": f"{patients['name'][0]['given'][0]} {patients['name'][0]['family']}"
            },
            "whenHandedOver": datetime.now().isoformat(),
            "quantity": {
                "value": float(medications_data.get("quantity", 1)),
                "unit": medications_data.get("unit", "unit")
            },
            "daysSupply": {
                "value": float(medications_data.get("daysSupply", 1)),
                "unit": "days"
            },
            "performer": [
                {
                    "actor": {
                        "display": medications_data.get("performer", "Unknown"),
                        "type": "Practitioner"
                    }
                }
            ],
            "dosageInstruction": [
                {
                    "text": medications_data.get("dosage", "As prescribed"),
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
                    "text": medications_data.get("notes", "")
                }
            ],
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }

        # Validar estructura FHIR
        md = medicationsDispense.model_validate(dispense)
        validated_dispense = md.model_dump()
        
        # Insertar en MongoDB
        result = medications_collection.insert_one(validated_dispense)
        if result.inserted_id:
            return "success", str(result.inserted_id)
        return "errorInserting", None
        
    except Exception as e:
        return f"error: {str(e)}", None

def Getpatientsmedicationss(patients_id: str):
    """Obtiene todos los medicamentos de un paciente"""
    try:
        # Verificar que el paciente existe primero
        status, _ = GetpatientsById(patients_id)
        if status != "success":
            return "patientsNotFound", None
            
        medicationss = list(medications_collection.find({
            "subject.reference": f"patients/{patients_id}"
        }).sort("whenHandedOver", -1))  # Ordenar por fecha descendente
        
        for med in medicationss:
            med["_id"] = str(med["_id"])
            # Convertir fechas a string para respuesta JSON
            if "whenHandedOver" in med:
                med["whenHandedOver"] = med["whenHandedOver"].isoformat()
            if "createdAt" in med:
                med["createdAt"] = med["createdAt"].isoformat()
            if "updatedAt" in med:
                med["updatedAt"] = med["updatedAt"].isoformat()
        
        return "success", medicationss
    except Exception as e:
        return f"error: {str(e)}", None
