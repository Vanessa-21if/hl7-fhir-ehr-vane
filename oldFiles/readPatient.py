from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from typing import Dict, List, Optional

def connect_to_mongodb(uri: str, db_name: str) -> Dict[str, MongoClient]:
    """
    Conexión segura a MongoDB para sistema de dispensación
    
    Args:
        uri: Cadena de conexión MongoDB
        db_name: Nombre de la base de datos
    
    Returns:
        Diccionario con las colecciones necesarias
    """
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client[db_name]
        return {
            'patients': db['pacientes'],
            'medications': db['dispensaciones']
        }
    except Exception as e:
        raise ConnectionError(f"Error de conexión a MongoDB: {str(e)}")

def get_patient_for_dispensing(collections: Dict, patient_id: str) -> Optional[Dict]:
    """
    Obtiene datos mínimos del paciente necesarios para dispensación
    
    Args:
        collections: Diccionario con colecciones MongoDB
        patient_id: ID del paciente
    
    Returns:
        Datos básicos del paciente o None si no se encuentra
    """
    try:
        return collections['patients'].find_one(
            {'_id': patient_id},
            {'name': 1, 'identifier': 1}  # Solo campos esenciales
        )
    except Exception as e:
        print(f"Error al buscar paciente: {str(e)}")
        return None

def register_medication_dispense(
    collections: Dict, 
    patient_id: str,
    medication_data: Dict
) -> Optional[str]:
    """
    Registra una dispensación de medicamento en el sistema
    
    Args:
        collections: Diccionario con colecciones MongoDB
        patient_id: ID del paciente
        medication_data: Datos del medicamento
        
    Returns:
        ID del registro creado o None en caso de error
    """
    required_fields = ['medicationName', 'quantity', 'daysSupply', 'dosage']
    if not all(field in medication_data for field in required_fields):
        print("Faltan campos requeridos en los datos del medicamento")
        return None
    
    try:
        dispense_record = {
            'resourceType': 'MedicationDispense',
            'status': 'completed',
            'medicationCodeableConcept': {
                'text': medication_data['medicationName']
            },
            'subject': {
                'reference': f'Patient/{patient_id}'
            },
            'quantity': {
                'value': float(medication_data['quantity']),
                'unit': 'unidades'
            },
            'daysSupply': {
                'value': float(medication_data['daysSupply']),
                'unit': 'días'
            },
            'dosageInstruction': [{
                'text': medication_data['dosage']
            }],
            'timestamp': datetime.now()
        }
        
        result = collections['medications'].insert_one(dispense_record)
        return str(result.inserted_id)
    except Exception as e:
        print(f"Error al registrar dispensación: {str(e)}")
        return None

if __name__ == '__main__':
    # Configuración - Debería venir de variables de entorno en producción
    CONFIG = {
        'MONGODB_URI': 'mongodb+srv://21vanessaaa:VANEifmer2025@sampleinformationservic.ceivw.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"
',
        'DB_NAME': 'SamplePatientService'
    }
    
    try:
        # 1. Conectar a MongoDB
        collections = connect_to_mongodb(CONFIG['MONGODB_URI'], CONFIG['DB_NAME'])
        
        # 2. Ejemplo: Obtener paciente (simulado)
        patient_id = '507f1f77bcf86cd799439011'  # En un sistema real vendría del request
        patient = get_patient_for_dispensing(collections, patient_id)
        
        if patient:
            # 3. Ejemplo: Registrar dispensación
            med_data = {
                'medicationName': 'Ibuprofeno 400mg',
                'quantity': 20,
                'daysSupply': 10,
                'dosage': '1 tableta cada 8 horas con alimentos'
            }
            
            dispense_id = register_medication_dispense(collections, patient_id, med_data)
            if dispense_id:
                print(f"Dispensación registrada con ID: {dispense_id}")
            else:
                print("Error al registrar la dispensación")
        else:
            print("Paciente no encontrado")
            
    except Exception as e:
        print(f"Error en el sistema: {str(e)}")
