import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Función para conectar a la base de datos MongoDB
def connect_to_mongodb(uri, db_name, collection_name):
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client[db_name]
    collection = db[collection_name]
    return collection

# Función para leer todos los pacientes de la colección
def read_patients_from_mongodb(collection):
    try:
        # Consultar todos los documentos en la colección
        patients = collection.find()
        
        # Convertir los documentos a una lista de diccionarios
        patient_list = list(patients)
        
        # Retornar la lista de pacientes
        return patient_list
    except Exception as e:
        print(f"Error al leer desde MongoDB: {e}")
        return None

# Función para mostrar los datos de los pacientes
def display_patients(patient_list):
    if patient_list:
        for patient in patient_list:
            print("Paciente:")
            print(f"  ID: {patient.get('_id')}")
            print(f"  Nombre: {patient.get('name', [{}])[0].get('given', [''])[0]} {patient.get('name', [{}])[0].get('family', '')}")
            print(f"  Género: {patient.get('gender', 'Desconocido')}")
            print(f"  Fecha de nacimiento: {patient.get('birthDate', 'Desconocida')}")
            print("-" * 30)
    else:
        print("No se encontraron pacientes en la base de datos.")

# Ejemplo de uso
if __name__ == "__main__":
    # Cadena de conexión a MongoDB (reemplaza con tu propia cadena de conexión)
    uri = "mongodb+srv://21vanessaaa:VANEifmer2025@sampleinformationservic.ceivw.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"

    # Nombre de la base de datos y la colección
    db_name = "SamplePatientService"
    collection_name = "patients"

    # Conectar a MongoDB
    collection = connect_to_mongodb(uri, db_name, collection_name)
    
    # Leer los pacientes de la colección
    patients = read_patients_from_mongodb(collection)
    
    # Mostrar los datos de los pacientes
    display_patients(patients)
