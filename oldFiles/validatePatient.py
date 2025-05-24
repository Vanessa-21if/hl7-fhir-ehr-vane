from fhir.resources.patient import Patient
from fhir.resources.medicationdispense import MedicationDispense
import json
from datetime import datetime


def create_minimal_patient(identifier_system: str, identifier_value: str, 
                           given_name: str, family_name: str) -> dict:
    """
    Crea un recurso Patient FHIR con datos mínimos para dispensación
    
    Args:
        identifier_system: Sistema de identificación (ej: 'http://cedula')
        identifier_value: Valor del identificador
        given_name: Nombre del paciente
        family_name: Apellido del paciente
    
    Returns:
        Diccionario con recurso Patient FHIR validado
    """
    patient_data = {
        "resourceType": "Patient",
        "identifier": [{
            "system": identifier_system,
            "value": identifier_value
        }],
        "name": [{
            "given": [given_name],
            "family": family_name
        }]
    }
    
    # Validar con modelo FHIR
    return Patient.model_validate(patient_data).model_dump()


def create_medication_dispense(patient_id: str, medication_name: str, 
                               quantity: float, days_supply: float, 
                               dosage: str) -> dict:
    """
    Crea un recurso MedicationDispense FHIR sincronizado con backend
    
    Args:
        patient_id: ID del paciente
        medication_name: Nombre del medicamento
        quantity: Cantidad dispensada
        days_supply: Días de tratamiento
        dosage: Instrucciones de dosificación
    
    Returns:
        Diccionario con recurso MedicationDispense FHIR validado y sincronizado
    """
    dispense_data = {
        "resourceType": "MedicationDispense",
        "status": "completed",
        "medicationCodeableConcept": {
            "text": medication_name
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "quantity": {
            "value": float(quantity),
            "unit": "unidades"
        },
        "daysSupply": {
            "value": float(days_supply),
            "unit": "días"
        },
        "dosageInstruction": [{
            "text": dosage
        }],
        # Fecha estandarizada usada en tu backend
        "extension": [{
            "url": "http://hl7.org/fhir/StructureDefinition/createdAt",
            "valueDateTime": datetime.now().isoformat()
        }]
    }

    # Validar con modelo FHIR
    return MedicationDispense.model_validate(dispense_data).model_dump()


if __name__ == "__main__":
    # Ejemplo 1: Crear paciente mínimo
    minimal_patient = create_minimal_patient(
        identifier_system="http://cedula",
        identifier_value="1020713756",
        given_name="Vanessa",
        family_name="Almonacid"
    )
    print("Paciente mínimo FHIR:")
    print(json.dumps(minimal_patient, indent=2))
    
    # Ejemplo 2: Crear dispensación de medicamento
    medication_dispense = create_medication_dispense(
        patient_id="507f1f77bcf86cd799439011",
        medication_name="Paracetamol 500mg",
        quantity=30,
        days_supply=10,
        dosage="1 tableta cada 8 horas"
    )
    print("\nDispensación FHIR:")
    print(json.dumps(medication_dispense, indent=2))
