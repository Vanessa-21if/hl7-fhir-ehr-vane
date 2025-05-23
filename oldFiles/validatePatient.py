from fhir.resources.patient import Patient
import json

# Ejemplo de uso
if __name__ == "__main__":
    # JSON string correspondiente al artefacto Patient de HL7 FHIR
    patient_json = '''
    {
      "resourceType": "Patient",
      "identifier": [
        {
          "system": "http://cedula",
          "value": "1020713756"
        },
        {
          "system": "http://pasaporte",
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

    pat = Patient.model_validate(json.loads(patient_json))
    print("JSON:: ",pat.model_dump())
