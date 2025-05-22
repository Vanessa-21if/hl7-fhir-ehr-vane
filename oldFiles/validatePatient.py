from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.address import Address
import json
from typing import List, Dict, Optional
from pydantic import ValidationError
from datetime import date

class FHIRPatientValidator:
    """Clase para validar y manipular recursos Patient FHIR"""
    
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
            return Patient.model_validate(patient_data)
        except ValidationError as e:
            print(f"❌ Error de validación FHIR: {e}")
            return None

    @staticmethod
    def create_patient(
        identifiers: List[Dict],
        names: List[Dict],
        telecom: List[Dict],
        gender: str,
        birth_date: str,
        addresses: List[Dict]
    ) -> Optional[Patient]:
        """
        Crea un recurso Patient FHIR estructurado
        
        Args:
            identifiers: Lista de identificadores
            names: Lista de nombres
            telecom: Datos de contacto
            gender: Género (male|female|other|unknown)
            birth_date: Fecha de nacimiento (YYYY-MM-DD)
            addresses: Lista de direcciones
            
        Returns:
            Objeto Patient válido o None si hay error
        """
        try:
            # Validar fecha de nacimiento
            birth_date = date.fromisoformat(birth_date)
            
            patient_data = {
                "resourceType": "Patient",
                "identifier": [Identifier.model_validate(i) for i in identifiers],
                "name": [HumanName.model_validate(n) for n in names],
                "telecom": [ContactPoint.model_validate(t) for t in telecom],
                "gender": gender,
                "birthDate": birth_date.isoformat(),
                "address": [Address.model_validate(a) for a in addresses]
            }
            
            return Patient.model_validate(patient_data)
        except ValueError as e:
            print(f"❌ Error en formato de fecha: {e}")
        except ValidationError as e:
            print(f"❌ Error de validación FHIR: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            
        return None

    @staticmethod
    def patient_to_json(patient: Patient) -> str:
        """Convierte un objeto Patient a JSON string"""
        return json.dumps(patient.model_dump(), indent=2)


# Ejemplo de uso mejorado
if __name__ == "__main__":
    print("=== Validador FHIR Patient ===")
    
    # Ejemplo 1: Validación desde JSON string
    patient_json = '''
    {
      "resourceType": "Patient",
      "identifier": [
        {
          "system": "http://cedula",
          "value": "1020713756",
          "type": {
            "coding": [{
              "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
              "code": "NN"
            }]
          }
        }
      ],
      "name": [{
        "use": "official",
        "family": "Duarte",
        "given": ["Mario", "Enrique"]
      }],
      "telecom": [
        {
          "system": "phone",
          "value": "3142279487",
          "use": "home"
        }
      ],
      "gender": "male",
      "birthDate": "1986-02-25",
      "address": [{
        "use": "home",
        "line": ["Cra 55A # 167A - 30"],
        "city": "Bogotá",
        "state": "Cundinamarca",
        "postalCode": "11156",
        "country": "Colombia"
      }]
    }
    '''
    
    print("\n1. Validación desde JSON:")
    patient_data = json.loads(patient_json)
    patient = FHIRPatientValidator.validate_patient(patient_data)
    
    if patient:
        print(FHIRPatientValidator.patient_to_json(patient))
    
    # Ejemplo 2: Creación estructurada
    print("\n2. Creación estructurada:")
    new_patient = FHIRPatientValidator.create_patient(
        identifiers=[{
            "system": "http://pasaporte",
            "value": "AQ123456789",
            "type": {
                "text": "Pasaporte"
            }
        }],
        names=[{
            "use": "official",
            "family": "Pérez",
            "given": ["Ana", "María"]
        }],
        telecom=[{
            "system": "email",
            "value": "ana.perez@example.com"
        }],
        gender="female",
        birth_date="1990-05-15",
        addresses=[{
            "city": "Medellín",
            "country": "Colombia"
        }]
    )
    
    if new_patient:
        print(FHIRPatientValidator.patient_to_json(new_patient))
