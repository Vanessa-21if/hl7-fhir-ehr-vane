from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Función para conectar a la base de datos MongoDB
def connect_to_mongodb(uri, db_name, collection_name):
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client[db_name]
    collection = db[collection_name]
    return collection

# Función para buscar pacientes por un identifier específico
def find_patient_by_identifier(collection, identifier_type, identifier_value):
    try:
        # Consultar el documento que coincida con el identifier
        query = {
            "identifier": {
                "$elemMatch": {
                    "type": identifier_type,
                    "value": identifier_value
                }
            }
        }
        patient = collection.find_one(query)
        
        # Retornar el paciente encontrado
        return patient
    except Exception as e:
        print(f"Error al buscar en MongoDB: {e}")
        return None

# Función para mostrar los datos de un paciente
def display_patient(patient):
    if patient:
        print("Paciente encontrado:")
        print(f"  ID: {patient.get('_id')}")
        print(f"  Nombre: {patient.get('name', [{}])[0].get('given', [''])[0]} {patient.get('name', [{}])[0].get('family', '')}")
        print(f"  Género: {patient.get('gender', 'Desconocido')}")
        print(f"  Fecha de nacimiento: {patient.get('birthDate', 'Desconocida')}")
        print("  Identificadores:")
        for identifier in patient.get("identifier", []):
            print(f"    Type: {identifier.get('type')}, Valor: {identifier.get('value')}")
    else:
        print("No se encontró ningún paciente con el identifier especificado.")

# Ejemplo de uso
if __name__ == "__main__":
    # Cadena de conexión a MongoDB (reemplaza con tu propia cadena de conexión)
    uri = "mongodb+srv://21vanessaaa:VANEifmer2025@sampleinformationservic.ceivw.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"

    # Nombre de la base de datos y la colección
    db_name = "SamplePatientService"
    collection_name = "patients"

    # Conectar a MongoDB
    collection = connect_to_mongodb(uri, db_name, collection_name)
    
    # Identifier específico a buscar (reemplaza con los valores que desees)
    identifier_type = "cc"
    identifier_value = "1020713756"
    
    # Buscar el paciente por identifier
    patient = find_patient_by_identifier(collection, identifier_type, identifier_value)
    
    # Mostrar los datos del paciente encontrado
    display_patient(patient)
