import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime


def connect_to_mongodb(uri: str, db_name: str) -> dict:
    """
    Conexión segura a MongoDB para sistema de dispensación
    """
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client[db_name]
        return {
            'patients': db['patients'],
            'medications': db['medications']
        }
    except Exception as e:
        raise ConnectionError(f"Error de conexión a MongoDB: {str(e)}")


def save_minimal_patient(collections: dict, identifier: dict, name: dict) -> str:
    """
    Guarda un paciente con datos mínimos para dispensación
    """
    patient_data = {
        "resourceType": "Patient",
        "identifier": [{
            "system": identifier['system'],
            "value": identifier['value']
        }],
        "name": [{
            "given": [name['given']],
            "family": name['family']
        }],
        "createdAt": datetime.now().isoformat()
    }

    result = collections['patients'].insert_one(patient_data)
    return str(result.inserted_id)


def save_medication_dispense(collections: dict, dispense_data: dict) -> str:
    """
    Registra una dispensación de medicamento con estructura FHIR
    """
    medication_record = {
        "resourceType": "MedicationDispense",
        "status": "completed",
        "medicationCodeableConcept": {
            "text": dispense_data['medication_name']
        },
        "subject": {
            "reference": f"Patient/{dispense_data['patient_id']}"
        },
        "quantity": {
            "value": float(dispense_data['quantity']),
            "unit": "unidades"
        },
        "daysSupply": {
            "value": float(dispense_data['days_supply']),
            "unit": "días"
        },
        "dosageInstruction": [{
            "text": dispense_data['dosage']
        }],
        "extension": [{
            "url": "http://hl7.org/fhir/StructureDefinition/createdAt",
            "valueDateTime": datetime.now().isoformat()
        }]
    }

    result = collections['medications'].insert_one(medication_record)
    return str(result.inserted_id)


if __name__ == "__main__":
    # Configuración - usar variables de entorno en producción
    CONFIG = {
        'MONGODB_URI': 'mongodb+srv://21vanessaaa:VANEifmer2025@sampleinformationservic.ceivw.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService',
        'DB_NAME': 'SamplePatientService'
    }

    try:
        # 1. Conectar a MongoDB
        collections = connect_to_mongodb(CONFIG['MONGODB_URI'], CONFIG['DB_NAME'])

        # 2. Registrar paciente mínimo
        patient_id = save_minimal_patient(
            collections,
            identifier={'system': 'http://cedula', 'value': '1020713756'},
            name={'given': 'Mario', 'family': 'Duarte'}
        )
        print(f"Paciente registrado con ID: {patient_id}")

        # 3. Registrar dispensación
        dispense_id = save_medication_dispense(
            collections,
            {
                'patient_id': patient_id,
                'medication_name': 'Paracetamol 500mg',
                'quantity': 30,
                'days_supply': 10,
                'dosage': '1 tableta cada 8 horas'
            }
        )
        print(f"Dispensación registrada con ID: {dispense_id}")

    except Exception as e:
        print(f"Error en el sistema: {str(e)}")
