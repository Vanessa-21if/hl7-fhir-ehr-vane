import json
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Función para conectar a la base de datos MongoDB
def connect_to_mongodb(uri, db_name, collection_name):
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client[db_name]
    collection = db[collection_name]
    return collection

# Función para guardar el JSON en MongoDB
def save_patient_to_mongodb(patient_json, collection):
    try:
        # Convertir el JSON string a un diccionario de Python
        patient_data = json.loads(patient_json)

        # Insertar el documento en la colección de MongoDB
        result = collection.insert_one(patient_data)

        # Retornar el ID del documento insertado
        return result.inserted_id
    except Exception as e:
        print(f"Error al guardar en MongoDB: {e}")
        return None

# Ejemplo de uso
if __name__ == "__main__":
    # Cadena de conexión a MongoDB (reemplaza con tu propia cadena de conexión)
    uri = "mongodb+srv://21vanessaaa:VANEifmer2025@sampleinformationservic.ceivw.mongodb.net/?retryWrites=true&w=majority&appName=SampleInformationService"

    # Nombre de la base de datos y la colección
    db_name = "SamplePatientService"
    collection_name = "patients"

    # Conectar a MongoDB
    collection = connect_to_mongodb(uri, db_name, collection_name)

    # JSON string correspondiente al artefacto Patient de HL7 FHIR
    patient_json = f'''
    {
      "resourceType": "Patient",
      "identifier": [
        {
          "type": "cc",
          "value": "1020713756"
        },
        {
          "type": "pp",
          "value": "AQ123456789"
        }
      ],
      "name": [
        {
          "use": "official",
          "text": "Mario Enrique Duarte",
          "family": "Duarte",
          "given": [
            "Mario",
            "Enrique"
          ]
        }
      ],
      "telecom": [
        {
          "system": "phone",
          "value": "3142279487",
          "use": "home"
        },
        {
          "system": "email",
          "value": "mardugo@gmail.com",
          "use": "home"
        }
      ],
      "gender": "male",
      "birthDate": "1986-02-25",
      "address": [
        {
          "use": "home",
          "line": [
            "Cra 55A # 167A - 30"
          ],
          "city": "Bogotá",
          "state": "Cundinamarca",
          "postalCode": "11156",
          "country": "Colombia"
        }
      ]
    }
    '''

    # Guardar el JSON en MongoDB
    inserted_id = save_patient_to_mongodb(patient_json, collection)

    if inserted_id:
        print(f"Paciente guardado con ID: {inserted_id}")
    else:
        print("No se pudo guardar el paciente.")
