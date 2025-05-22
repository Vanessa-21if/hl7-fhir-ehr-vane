from fhir.resources.patient import Patient
from fhir.resources.medicationdispense import MedicationDispense
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.address import Address
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.dosage import Dosage
from fhir.resources.quantity import Quantity
import json
from typing import List, Dict, Optional, Union
from pydantic import ValidationError
from datetime import date, datetime
from enum import Enum

class MedicationStatus(str, Enum):
    """Estados posibles para un MedicationDispense"""
    PREPARATION = "preparation"
    IN_PROGRESS = "in-progress"
    CANCELLED = "cancelled"
    ON_HOLD = "on-hold"
    COMPLETED = "completed"
    ENTERED_IN_ERROR = "entered-in-error"
    STOPPED = "stopped"
    UNKNOWN = "unknown"

class FHIRValidator:
    """Clase para validar recursos FHIR de pacientes y medicamentos"""
    
    # ===== VALIDACIÓN DE PACIENTES =====
    @staticmethod
    def validate_patient(patient_data: Dict) -> Optional[Patient]:
        """
        Valida un diccionario como recurso Patient FHIR válido
        
        Args:
            patient_data: Diccionario con datos del paciente
            
        Returns:
            Objeto Patient válido o None si hay error
        """
        try:
            # Validación de componentes FHIR
            if "identifier" in patient_data:
                patient_data["identifier"] = [Identifier.model_validate(i) for i in patient_data["identifier"]]
            if "name" in patient_data:
                patient_data["name"] = [HumanName.model_validate(n) for n in patient_data["name"]]
            if "telecom" in patient_data:
                patient_data["telecom"] = [ContactPoint.model_validate(t) for t in patient_data["telecom"]]
            if "address" in patient_data:
                patient_data["address"] = [Address.model_validate(a) for a in patient_data["address"]]
            
            return Patient.model_validate(patient_data)
        except ValidationError as e:
            print(f"❌ Error de validación FHIR (Patient): {e}")
            return None

    # ===== VALIDACIÓN DE MEDICAMENTOS =====
    @staticmethod
    def validate_medication(medication_data: Dict) -> Optional[MedicationDispense]:
        """
        Valida un diccionario como recurso MedicationDispense FHIR válido
        Cumple con los requisitos de la historia de usuario
        
        Args:
            medication_data: Diccionario con datos del medicamento
            
        Returns:
            Objeto MedicationDispense válido o None si hay error
        """
        try:
            # Validación de campos requeridos para la historia de usuario
            required_fields = [
                "medicationCodeableConcept",
                "subject",
                "quantity",
                "daysSupply",
                "dosageInstruction"
            ]
            
            for field in required_fields:
                if field not in medication_data:
                    raise ValueError(f"Campo requerido faltante: {field}")
            
            # Validación de componentes FHIR
            if "medicationCodeableConcept" in medication_data:
                medication_data["medicationCodeableConcept"] = CodeableConcept.model_validate(
                    medication_data["medicationCodeableConcept"]
                )
            
            if "quantity" in medication_data:
                medication_data["quantity"] = Quantity.model_validate(
                    medication_data["quantity"]
                )
            
            if "dosageInstruction" in medication_data:
                medication_data["dosageInstruction"] = [
                    Dosage.model_validate(d) for d in medication_data["dosageInstruction"]
                ]
            
            # Establecer valores por defecto para la historia de usuario
            if "status" not in medication_data:
                medication_data["status"] = MedicationStatus.COMPLETED.value
                
            if "whenHandedOver" not in medication_data:
                medication_data["whenHandedOver"] = datetime.utcnow().isoformat()
            
            return MedicationDispense.model_validate(medication_data)
        except ValidationError as e:
            print(f"❌ Error de validación FHIR (MedicationDispense): {e}")
            return None
        except ValueError as e:
            print(f"❌ Error en datos de medicamento: {e}")
            return None

    # ===== MÉTODOS DE CREACIÓN ESTRUCTURADA =====
    @staticmethod
    def create_medication(
        medication_name: str,
        patient_reference: str,
        quantity: float,
        quantity_unit: str,
        days_supply: float,
        dosage_text: str,
        performer: Optional[str] = None,
        status: MedicationStatus = MedicationStatus.COMPLETED
    ) -> Optional[Dict]:
        """
        Crea un recurso MedicationDispense válido para la historia de usuario
        
        Args:
            medication_name: Nombre del medicamento
            patient_reference: Referencia al paciente (Patient/[id])
            quantity: Cantidad del medicamento
            quantity_unit: Unidad de medida (tabletas, ml, etc.)
            days_supply: Días de tratamiento
            dosage_text: Instrucciones de dosificación
            performer: Nombre del profesional que entrega
            status: Estado de la dispensación
            
        Returns:
            Diccionario con MedicationDispense válido o None si hay error
        """
        try:
            medication = {
                "resourceType": "MedicationDispense",
                "status": status.value,
                "medicationCodeableConcept": {
                    "text": medication_name
                },
                "subject": {
                    "reference": patient_reference
                },
                "quantity": {
                    "value": quantity,
                    "unit": quantity_unit
                },
                "daysSupply": {
                    "value": days_supply,
                    "unit": "días"
                },
                "dosageInstruction": [{
                    "text": dosage_text
                }],
                "whenHandedOver": datetime.utcnow().isoformat()
            }
            
            if performer:
                medication["performer"] = [{
                    "actor": {
                        "display": performer
                    }
                }]
            
            # Validar la estructura creada
            if FHIRValidator.validate_medication(medication):
                return medication
            return None
                
        except Exception as e:
            print(f"❌ Error al crear medicamento: {e}")
            return None

    # ===== UTILIDADES =====
    @staticmethod
    def resource_to_json(resource: Union[Patient, MedicationDispense]) -> str:
        """Convierte un recurso FHIR a JSON string formateado"""
        return json.dumps(resource.model_dump(), indent=2, ensure_ascii=False)


# Ejemplo de uso que cumple con la historia de usuario
if __name__ == "__main__":
    print("=== Validador FHIR para Historia Clínica Electrónica ===")
    
    # 1. Validar paciente
    print("\n1. Validación de paciente:")
    patient_data = {
        "resourceType": "Patient",
        "identifier": [{
            "system": "http://cedula",
            "value": "1020713756",
            "type": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                    "code": "NN"
                }]
            }
        }],
        "name": [{
            "use": "official",
            "family": "Duarte",
            "given": ["Mario", "Enrique"]
        }],
        "gender": "male",
        "birthDate": "1986-02-25"
    }
    
    patient = FHIRValidator.validate_patient(patient_data)
    if patient:
        print("✅ Paciente válido")
        print(FHIRValidator.resource_to_json(patient))
    
    # 2. Validar medicamento (cumpliendo historia de usuario)
    print("\n2. Validación de medicamento:")
    medication_data = {
        "resourceType": "MedicationDispense",
        "medicationCodeableConcept": {
            "text": "Paracetamol 500mg",
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "387517004"
            }]
        },
        "subject": {
            "reference": "Patient/12345"
        },
        "quantity": {
            "value": 30,
            "unit": "tabletas"
        },
        "daysSupply": {
            "value": 10,
            "unit": "días"
        },
        "dosageInstruction": [{
            "text": "Tomar 1 tableta cada 8 horas"
        }],
        "performer": [{
            "actor": {
                "display": "Dr. Rodríguez"
            }
        }]
    }
    
    medication = FHIRValidator.validate_medication(medication_data)
    if medication:
        print("✅ Medicamento válido")
        print(FHIRValidator.resource_to_json(medication))
    
    # 3. Creación estructurada de medicamento
    print("\n3. Creación de medicamento para historia de usuario:")
    new_med = FHIRValidator.create_medication(
        medication_name="Ibuprofeno 400mg",
        patient_reference="Patient/12345",
        quantity=20,
        quantity_unit="tabletas",
        days_supply=5,
        dosage_text="Tomar 1 tableta cada 12 horas con alimentos",
        performer="Dra. Gómez"
    )
    
    if new_med:
        print("✅ Medicamento creado correctamente")
        print(json.dumps(new_med, indent=2))
